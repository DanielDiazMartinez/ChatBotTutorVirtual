# Etapa 1: Construcción
FROM node:18 as build

# Establecer directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar package.json y package-lock.json para instalar dependencias
COPY package.json package-lock.json ./

# Instalar dependencias
RUN npm install

# Copiar el código fuente de la aplicación Angular
COPY . .

# Construir la aplicación Angular para producción
RUN npm run build --prod

# Etapa 2: Servidor ligero para servir la aplicación Angular
FROM nginx:stable-alpine

# Copiar los archivos construidos desde la etapa anterior
COPY --from=build /app/dist/browser /usr/share/nginx/html

# Copiar archivo de configuración personalizada de NGINX si es necesario
# COPY nginx.conf /etc/nginx/nginx.conf

# Exponer el puerto 80
EXPOSE 80

# Comando por defecto para iniciar NGINX
CMD ["nginx", "-g", "daemon off;"]
