# Etapa de construcción
FROM node:22 AS build

# Establece el directorio de trabajo
WORKDIR /app

# Copia solo los archivos necesarios para instalar las dependencias
COPY package.json package-lock.json ./

# Instala las dependencias
RUN npm install

# Copia el resto del código de la aplicación
COPY . .

# Compila la aplicación para producción
RUN npm run build

# Etapa de producción
FROM nginx:alpine

# Copia el archivo de configuración de Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copia los archivos compilados desde la etapa de construcción
COPY --from=build /app/dist /usr/share/nginx/html

# Expone el puerto en el que se ejecutará la aplicación
EXPOSE 80

# Comando para ejecutar Nginx
CMD ["nginx", "-g", "daemon off;"]