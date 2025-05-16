export interface User {
  id: number;
  email: string;
  full_name: string;
  role: 'admin' | 'teacher' | 'student';
}

export interface UserCreate {
  email: string;
  password: string;
  full_name: string;
  role: 'admin' | 'teacher' | 'student';
}

export interface UserLogin {
  email: string;
  password: string;
}
