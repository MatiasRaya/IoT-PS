from flask import Flask, redirect, render_template, request

app = Flask(__name__)

tareas = []

@app.route("/")
def home():
    return render_template("index.html", tareas=tareas)

@app.route("/agregar", methods=["GET", "POST"])
def agregar():
    if request.method == "GET":
        return render_template("agregar.html")
    else:
        tarea = request.form.get("tarea")
        tareas.append(tarea)
        return redirect("/")


if __name__ == "__main__":
    app.run(port=5001,debug=True)