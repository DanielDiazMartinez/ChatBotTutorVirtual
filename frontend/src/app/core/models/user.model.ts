export interface User {
  id: number;
  email: string;
  name: string;
  role: 'admin' | 'teacher' | 'student';
}

export interface UserCreate {
  email: string;
  password: string;
  name: string;
  role: 'admin' | 'teacher' | 'student';
}

export interface UserLogin {
  email: string;
  password: string;
}
