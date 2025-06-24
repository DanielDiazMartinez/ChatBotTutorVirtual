from sqlalchemy.orm import Session
from ..models.schemas import SubjectCreate
from app.crud import crud_subject

def create_subject(db: Session, subject: SubjectCreate) -> dict:
    """Crea una nueva asignatura"""
    
    # Verificar si ya existe una asignatura con ese código usando CRUD
    existing_subject = crud_subject.get_subject_by_code(db, subject.code)
    if existing_subject:
        return {
            "error": "Ya existe una asignatura con ese código",
            "status": 400
        }
        
    # Crear la nueva asignatura usando CRUD
    db_subject = crud_subject.create_subject(
        db=db,
        name=subject.name,
        code=subject.code,
        description=subject.description
    )
    
    return {
        "id": db_subject.id,
        "name": db_subject.name,
        "code": db_subject.code,
        "description": db_subject.description,
        "summary": db_subject.summary,
        "created_at": db_subject.created_at
    }

def get_subject_by_id(db: Session, subject_id: int) -> dict:
    """Obtiene una asignatura por su ID"""
    db_subject = crud_subject.get_subject_by_id(db, subject_id)
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
        "summary": db_subject.summary,
        "created_at": db_subject.created_at,
        "teachers": teachers,
        "students": students,
        "teacher_count": teacher_count,
        "student_count": student_count,
        "document_count": crud_subject.count_documents_by_subject_id(db, subject_id)
    }
    
def get_all_subjects(db: Session) -> list[dict]:
    """Obtiene todas las asignaturas"""
    subjects = crud_subject.get_all_subjects(db)
    return [
        {
            "id": subject.id,
            "name": subject.name,
            "code": subject.code,
            "description": subject.description,
            "summary": subject.summary,
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
            "student_count": len([user for user in subject.users if user.role == "student"]) if subject.users else 0,
            "document_count": crud_subject.count_documents_by_subject_id(db, subject.id)
        }
        for subject in subjects
    ]

def update_subject(db: Session, subject_id: int, subject: SubjectCreate) -> dict:
    """Actualiza una asignatura existente"""
    # Usar CRUD para actualizar la asignatura
    db_subject = crud_subject.update_subject(
        db=db,
        subject_id=subject_id,
        name=subject.name,
        code=subject.code,
        description=subject.description
    )
    if not db_subject:
        return None
    
    # Preparar la respuesta con información de usuarios
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
        "summary": db_subject.summary,
        "created_at": db_subject.created_at,
        "teachers": teachers,
        "students": students,
        "teacher_count": teacher_count,
        "student_count": student_count
    }

def delete_subject(db: Session, subject_id: int) -> bool:
    """Elimina una asignatura"""
    return crud_subject.delete_subject(db, subject_id)

def add_user_to_subject(db: Session, subject_id: int, user_id: int) -> bool:
    """Agrega un usuario a una asignatura"""
    print(f"Intentando agregar: subject_id={subject_id}, user_id={user_id}")

    db_subject = crud_subject.get_subject_by_id(db, subject_id)
    db_user = crud_subject.get_user_by_id(db, user_id)
    
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
        success = crud_subject.add_user_to_subject(db, db_subject, db_user)
        if success:
            print(f"Usuario ({db_user.role}) agregado correctamente")
        else:
            print(f"El usuario ya está en la asignatura")
        return success
    except Exception as e:
        print(f"Error al agregar usuario: {str(e)}")
        return False

def add_multiple_users_to_subject(db: Session, subject_id: int, user_ids: list[int]) -> dict:
    """
    Agrega múltiples usuarios a una asignatura
    """
    db_subject = crud_subject.get_subject_by_id(db, subject_id)
    if not db_subject:
        return {"success": False, "error": "Asignatura no encontrada", "added": [], "failed": user_ids}
    
    results = {
        "success": False,
        "added": [],
        "failed": []
    }
    
    for user_id in user_ids:
        try:
            db_user = crud_subject.get_user_by_id(db, user_id)
            
            if not db_user:
                results["failed"].append({"id": user_id, "reason": "Usuario no encontrado"})
                continue
                
            if db_user.role == "admin":
                results["failed"].append({"id": user_id, "reason": "Los administradores no pueden ser añadidos a asignaturas"})
                continue
                
            if crud_subject.add_user_to_subject(db, db_subject, db_user):
                results["added"].append({"id": user_id, "role": db_user.role})
            else:
                results["failed"].append({"id": user_id, "reason": f"El {db_user.role} ya está asignado a esta asignatura"})
                
        except Exception as e:
            results["failed"].append({"id": user_id, "reason": str(e)})
    
    if results["added"]:
        results["success"] = True
    else:
        results["error"] = "No se pudo agregar ningún usuario"
            
    return results

def remove_multiple_users_from_subject(db: Session, subject_id: int, user_ids: list[int]) -> dict:
    """
    Elimina múltiples usuarios de una asignatura
    """
    db_subject = crud_subject.get_subject_by_id(db, subject_id)
    if not db_subject:
        return {"success": False, "error": "Asignatura no encontrada", "removed": [], "failed": user_ids}
    
    results = {
        "success": False,
        "removed": [],
        "failed": []
    }
    
    for user_id in user_ids:
        try:
            db_user = crud_subject.get_user_by_id(db, user_id)
            
            if not db_user:
                results["failed"].append({"id": user_id, "reason": "Usuario no encontrado"})
                continue
                
            if crud_subject.remove_user_from_subject(db, db_subject, db_user):
                results["removed"].append({"id": user_id, "role": db_user.role})
            else:
                results["failed"].append({"id": user_id, "reason": "Usuario no asociado a la asignatura"})
                
        except Exception as e:
            results["failed"].append({"id": user_id, "reason": str(e)})
    
    if results["removed"]:
        results["success"] = True
    else:
        results["error"] = "No se pudo eliminar ningún usuario"
            
    return results

def get_subject_documents(db: Session, subject_id: int):
    """Obtiene todos los documentos asociados a una asignatura"""
    subject = crud_subject.get_subject_by_id(db, subject_id)
    if not subject:
        return None
        
    documents = crud_subject.get_documents_by_subject_id(db, subject_id)
    return documents

def get_subject_users(db: Session, subject_id: int) -> dict:
    """Obtiene todos los usuarios asociados a una asignatura"""
    db_subject = crud_subject.get_subject_by_id(db, subject_id)
    if not db_subject:
        return None
    
    # Preparar la lista de usuarios
    users = [
        {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "created_at": user.created_at
        }
        for user in db_subject.users
    ] if db_subject.users else []
    
    # Separar usuarios por rol
    teachers = [user for user in users if user["role"] == "teacher"]
    students = [user for user in users if user["role"] == "student"]
    
    return {
        "subject_id": db_subject.id,
        "subject_name": db_subject.name,
        "subject_code": db_subject.code,
        "teachers": teachers,
        "students": students,
        "teacher_count": len(teachers),
        "student_count": len(students),
        "total_users": len(users)
    }
