from http.server import BaseHTTPRequestHandler, HTTPServer #Clases para levantar servidores http
import json
from urllib.parse import urlparse
from conexion import get_connection #Archivo de la conexion y funcion donde se hizo la conexion
import simplejson as json #libreria para importar correctamemte el json

class servidorHttp(BaseHTTPRequestHandler):

    #Metodo para que el navegador reciba los encabezados 
    def do_OPTIONS(self): 
        self.send_response(200)
        self.send_header("Access-control-Allow-Origin", "*")
        self.send_header("Access-control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-control-Allow-Headers", "Content-type")
        self.end_headers()

    #Api para solicitudes POST - create en el crud
    def do_POST(self): 
        if self.path == "/products": 
            content_length = int(self.headers['Content-length'])
            body=self.rfile.read(content_length)
            data= json.loads(body)

            #Validacion de datos negativos
            if data ["price"]<0 or data ["stock"]<0: 
                self.send_response(400)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"error":"El precio y el stock no deben de ser negativos"}).encode("utf-8"))
                return 
            
            conexion=get_connection()
            cursor=conexion.cursor()
            cursor.execute("INSERT INTO products(name, price, stock) VALUES (%s, %s, %s)", 
                           (data["name"], data["price"], data["stock"]))
            conexion.commit()
            conexion.close()

            self.send_response(201)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"message":"Producto creado"}).encode("utf-8"))

    #Api para solicitudes get - listar y buscar por id       
    def do_GET(self): 
        #Pagina de inicio del servidor
        parsed=urlparse(self.path)
        if parsed.path=="/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write("<h1>Bienvenido al servidor</h1>".encode("utf-8"))

        #Listar productos
        elif parsed.path==("/products"):
            conexion=get_connection()
            cursor=conexion.cursor(dictionary=True)
            cursor.execute("SELECT * FROM products")
            productos=cursor.fetchall()
            conexion.close()

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(productos).encode("utf-8"))

        #Obtener productos por id
        elif parsed.path.startswith("/products/"):
            id=int(parsed.path.split("/")[-1])
            conexion=get_connection()
            cursor=conexion.cursor(dictionary=True)
            cursor.execute("SELECT * FROM products WHERE id=%s", (id, ))
            producto=cursor.fetchone()
            conexion.close()

            self.send_response(200 if producto else 404)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            if producto: 
                self.wfile.write(json.dumps(producto).encode("utf-8"))
            else: 
                self.wfile.write(json.dumps({"error":"404 producto no encontrado"}).encode("utf-8"))

    #API para obtener peticiones PUT - editar registro
    def do_PUT(self):
        if self.path.startswith("/products/"):
            id=int(self.path.split("/")[-1])
            content_length=int(self.headers['Content-Length'])
            body=self.rfile.read(content_length)
            data=json.loads(body)

            #Validacion de datos negativos
            if data["price"]<0 or data["stock"]<0:
                self.send_response(400)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"error":"El precio y el stock no deben de ser negativos"}).encode("utf-8"))
                return 
            
            conexion=get_connection()
            cursor=conexion.cursor()
            cursor.execute("UPDATE products SET name=%s, price=%s, stock=%s WHERE id=%s", 
                           (data["name"], data["price"], data["stock"], id))
            conexion.commit()
            conexion.close()

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"message":"Producto actualizado"}).encode("utf-8"))
    
    #API pata solicitudes DELETE-eliminar un producto
    def do_DELETE(self): 
        if self.path.startswith("/products/"): 
            id=int(self.path.split("/")[-1])
            conexion=get_connection()
            cursor=conexion.cursor()
            cursor.execute("DELETE FROM products where id=%s", (id, ))
            conexion.commit()
            conexion.close()

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"message":"Producto eliminado"}).encode("utf-8"))

#Inicia el servidor
if __name__ == "__main__":
    server=HTTPServer(("localhost", 8000), servidorHttp)
    print("El servidor esta corriendo en http://localhost:8000")
    server.serve_forever()