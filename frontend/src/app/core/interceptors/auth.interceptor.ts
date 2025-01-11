import { HttpInterceptorFn } from '@angular/common/http';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  // Clonar la solicitud y agregar un encabezado de autorización
  const clonedRequest = req.clone({
    setHeaders: {
      Authorization: `Bearer your-token-here`, // Reemplaza con tu lógica de token
    },
  });

  // Pasar la solicitud clonada al siguiente interceptor o enviar al servidor
  return next(clonedRequest);
};
