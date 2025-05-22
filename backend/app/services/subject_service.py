from sqlalchemy.orm import Session
from sqlalchemy import and_
from ..models.models import Subject, User, user_subject, Document
from ..models.schemas import SubjectCreate

def create_subject(db: Session, subject: SubjectCreate) -> dict:
    """Crea una nueva asignatura"""
    
    # Primero verificamos si ya existe una asignatura con ese código
    existing_subject = db.query(Subject).filter(Subject.code == subject.code).first()
    if existing_subject:
        return {
            "error": "Ya existe una asignatura con ese código",
            "status": 400
        }
        
    # Si no existe, creamos la nueva asignatura
    db_subject = Subject(
        name=subject.name,
        code=subject.code,
        description=subject.description
    )
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)
    return {
        "id": db_subject.id,
        "name": db_subject.name,
        "code": db_subject.code,
        "description": db_subject.description,
        "created_at": db_subject.created_at
    }

def get_subject_by_id(db: Session, subject_id: int) -> dict:
    """Obtiene una asignatura por su ID"""
    db_subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not db_subject:
        return None
    
    # Obtener lista de usuarios
    users = [
        {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role
        }
        for user in db_subject.users
    ] if db_subject.users else []
    
    # Separar usuarios por rol
    teachers = [user for user in users if user["role"] == "teacher"]
    students = [user for user in users if user["role"] == "student"]
    
    # Añadir conteo de estudiantes y profesores
    teacher_count = len(teachers)
    student_count = len(students)
    
    return {
        "id": db_subject.id,
        "name": db_subject.name,
        "code": db_subject.code,
        "description": db_subject.description,
        "created_at": db_subject.created_at,
        "teachers": teachers,
        "students": students,
        "teacher_count": teacher_count,
        "student_count": student_count
    }
    
def get_all_subjects(db: Session) -> list[dict]:
    """Obtiene todas las asignaturas"""
    subjects = db.query(Subject).all()
    return [
        {
            "id": subject.id,
            "name": subject.name,
            "code": subject.code,
            "description": subject.description,
            "created_at": subject.created_at,
            "teachers": [
                {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role
                }
                for user in subject.users if user.role == "teacher"
            ],
            "students": [
                {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role
                }
                for user in subject.users if user.role == "student"
            ],
            "teacher_count": len([user for user in subject.users if user.role == "teacher"]) if subject.users else 0,
            "student_count": len([user for user in subject.users if user.role == "student"]) if subject.users else 0
        }
        for subject in subjects
    ]

def update_subject(db: Session, subject_id: int, subject: SubjectCreate) -> dict:
    """Actualiza una asignatura existente"""
    # Aquí obtenemos el objeto directamente ya que get_subject_by_id ahora devuelve un dict
    db_subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not db_subject:
        return None
    
    db_subject.name = subject.name
    db_subject.code = subject.code
    db_subject.description = subject.description
    
    db.commit()
    db.refresh(db_subject)
    
    # Preparamos la respuesta
    users = [
        {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role
        }
        for user in db_subject.users
    ] if db_subject.users else []
    
    # Separar usuarios por rol
    teachers = [user for user in users if user["role"] == "teacher"]
    students = [user for user in users if user["role"] == "student"]
    
    # Añadir conteo de estudiantes y profesores
    teacher_count = len(teachers)
    student_count = len(students)
    
    return {
        "id": db_subject.id,
        "name": db_subject.name,
        "code": db_subject.code,
        "description": db_subject.description,
        "created_at": db_subject.created_at,
        "teachers": teachers,
        "students": students,
        "teacher_count": teacher_count,
        "student_count": student_count
    }

def delete_subject(db: Session, subject_id: int) -> bool:
    """Elimina una asignatura"""
    db_subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not db_subject:
        return False
    
    db.delete(db_subject)
    db.commit()
    return True

def add_user_to_subject(db: Session, subject_id: int, user_id: int) -> bool:
    """Agrega un usuario a una asignatura"""
    print(f"Intentando agregar: subject_id={subject_id}, user_id={user_id}")

    db_subject = db.query(Subject).filter(Subject.id == subject_id).first()
    db_user = db.query(User).filter(User.id == user_id).first()
    
    print(f"Subject encontrado: {db_subject is not None}")
    print(f"User encontrado: {db_user is not None}")
    
    if not db_subject or not db_user:
        print("No se encontró asignatura o usuario")
        return False
    
    print(f"Rol del usuario: {db_user.role}")
    if db_user.role == "admin":
        print("El usuario es admin, operación no permitida")
        return False
    
    try:
        if db_user not in db_subject.users:
            db_subject.users.append(db_user)
            print(f"Usuario ({db_user.role}) agregado correctamente")
        else:
            print(f"El usuario ya está en la asignatura")
            return False
        
        db.commit()
        print("Commit realizado con éxito")
        return True
    except Exception as e:
        print(f"Error al agregar usuario: {str(e)}")
        db.rollback()
        return False

def add_multiple_users_to_subject(db: Session, subject_id: int, user_ids: list[int]) -> dict:
    """
    Agrega múltiples usuarios a una asignatura
    """
    db_subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not db_subject:
        return {"success": False, "error": "Asignatura no encontrada", "added": [], "failed": user_ids}
    
    results = {
        "success": False,
        "added": [],
        "failed": []
    }
    
    for user_id in user_ids:
        try:
            db_user = db.query(User).filter(User.id == user_id).first()
            
            if not db_user:
                results["failed"].append({"id": user_id, "reason": "Usuario no encontrado"})
                continue
                
            if db_user.role == "admin":
                results["failed"].append({"id": user_id, "reason": "Los administradores no pueden ser añadidos a asignaturas"})
                continue
                
            if db_user not in db_subject.users:
                db_subject.users.append(db_user)
                results["added"].append({"id": user_id, "role": db_user.role})
            else:
                results["failed"].append({"id": user_id, "reason": f"El {db_user.role} ya está asignado a esta asignatura"})
                
        except Exception as e:
            results["failed"].append({"id": user_id, "reason": str(e)})
    
    if results["added"]:
        try:
            db.commit()
            results["success"] = True
        except Exception as e:
            db.rollback()
            results["success"] = False
            results["error"] = str(e)
            results["failed"].extend(results["added"])
            results["added"] = []
    else:
        results["error"] = "No se pudo agregar ningún usuario"
            
    return results

def remove_multiple_users_from_subject(db: Session, subject_id: int, user_ids: list[int]) -> dict:
    """
    Elimina múltiples usuarios de una asignatura
    """
    db_subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not db_subject:
        return {"success": False, "error": "Asignatura no encontrada", "removed": [], "failed": user_ids}
    
    results = {
        "success": False,
        "removed": [],
        "failed": []
    }
    
    for user_id in user_ids:
        try:
            db_user = db.query(User).filter(User.id == user_id).first()
            
            if not db_user:
                results["failed"].append({"id": user_id, "reason": "Usuario no encontrado"})
                continue
                
            if db_user in db_subject.users:
                db_subject.users.remove(db_user)
                results["removed"].append({"id": user_id, "role": db_user.role})
            else:
                results["failed"].append({"id": user_id, "reason": "Usuario no asociado a la asignatura"})
                
        except Exception as e:
            results["failed"].append({"id": user_id, "reason": str(e)})
    
    if results["removed"]:
        try:
            db.commit()
            results["success"] = True
        except Exception as e:
            db.rollback()
            results["success"] = False
            results["error"] = str(e)
            results["failed"].extend(results["removed"])
            results["removed"] = []
    else:
        results["error"] = "No se pudo eliminar ningún usuario"
            
    return results

def get_subject_documents(db: Session, subject_id: int):
    """Obtiene todos los documentos asociados a una asignatura"""
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        return None
        
    documents = db.query(Document).filter(Document.subject_id == subject_id).all()
    return documents
