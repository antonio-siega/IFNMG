import json, os
from flask import Flask, request, jsonify
from flask_jwt_extended import(
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)

from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = "123456" #CHANGE BEFORE USING IN PRODUCTION CODE!!
jwt = JWTManager(app)

#lists for internal system use
tasks = []
users = []
usersRequiredFields = ["id", "username", "email", "password"]
tasksRequiredFields = ["id", "title", "status"]
tasksOptionalFields = ["description"]
    #user_id isn't present in tasksRequiredFields because we get it automatically from the JWT identity.
    #see register_task() for details.

tasksFilePath = 'tasks.json'
usersFilePath = 'users.json'

#=== INTERNAL FUNCTIONS ===#

def open_file(path):
    try:
        if not os.path.exists(path):
            with open(path, 'w') as file:
                file.write("[]") #initializing the json data list to prevent Flask
                                #from raising an error when opening the file later
        else:
            with open(path, "r", encoding='utf-8') as file:
                if path == tasksFilePath:
                    global tasks
                    tasks = json.load(file)
                elif path == usersFilePath:
                    global users
                    users = json.load(file)
    except Exception as e:
        print(f"Error opening {path}: {e}")

def save_file(path):
    try:
        with open(path, 'w', encoding='utf-8') as file:
            if path == tasksFilePath:
                json.dump(tasks, file, ensure_ascii=False, indent=4)
            elif path == usersFilePath:
                json.dump(users, file, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error saving {path}: {e}")

def msg_status_dict(message, status=200):
    return {"message": message, "status_code": status}

#validation for getting task data restricted to a certain user ID.
#returnIndex allows for the value returned to be only the task index instead of the task itself.
def get_protected_task(id, userId, returnIndex=0):
    task = [task for task in tasks if task["id"] == id]
    
    #checking if the task exists
    if len(task) == 0:
        return msg_status_dict("No task currently associated to specified task ID.")
        #OBS: we CANNOT use jsonify() here, since there is no active request context.
    else:
        task = task[0]
    
    #checking if the task actually belongs to the user trying to access it
    if task["user_id"] != userId:
        return msg_status_dict("Unauthorized access attempt to protected content.", 403)
    
    if returnIndex:
        return tasks.index(task)
    else:
        return task

#for validating user registrations
def user_data_validation(userData):
    for field in usersRequiredFields:
        if not userData.get(field, 0): #if key is empty or doesn't exist
            return msg_status_dict(f"Error registering user: field {field} is required.", 500)

    for user in users:
        if userData["id"] == user["id"]:
            return msg_status_dict("Error registering user: id already in use.", 500)
        elif userData["email"] == user["email"]:
            return msg_status_dict("Error registering user: e-mail already in use.", 500)
    
    if type(userData["id"]) is not int: #standardizing user id to be int.
        return msg_status_dict("Error registering user: id must be of type INT.", 500)
    
    for field in usersRequiredFields:
        if field == "id": #id doesn't need to be checked again
            continue
        else: #all fields except ID must be of type STR
            if type(userData[field]) is not str:
                return msg_status_dict(f"Error registering user: {field} must be of type STR.", 500)
    
    return 1 #everything is okay! :D

#for validating task registrations
def task_data_validation(taskData):
    for field in tasksRequiredFields:
        if not taskData.get(field, 0): #if key is empty or doesn't exist
            return msg_status_dict( f"Error registering task: field '{field}' is required.", 500)
            #OBS: we CANNOT use jsonify() here, since there is no active request context.
    
    for task in tasks:
        if task["id"] == taskData["id"]:
            return msg_status_dict("Error registering task: id already in use.", 500)
    
    if type(taskData["id"]) is not int: #standardizing task id to be int.
        return msg_status_dict("Error registering task: id must be of type INT.", 500)
    
    for field in tasksRequiredFields:
        if field == "id": 
            continue #id doesn't need to be checked again
        else:
            if type(taskData[field]) is not str: #all fields must be of type STR
                return msg_status_dict(f"Error registering task: field '{field}' must be of type STR.", 500)
    
    for field in tasksOptionalFields:
        if not taskData.get(field, 0): #if an optional field is missing, it's okay.
            continue
        else: #if the optional field is there, check if it is of the correct type
            if type(taskData[field]) is not str:
                return msg_status_dict(f"Error registering task: field '{field}' must be of type STR.", 500)
    
    return 1 #everything is okay! :D

#=== ENDPOINTS >>WITHOUT<< REQUIRED JWT AUTHENTICATION ===#

#User registration endpoint
@app.route('/register', methods=["POST"])
def register_user():
    try:
        userData = request.get_json()

        userDataValidation = user_data_validation(userData)
        if type(userDataValidation) is dict:
            return jsonify({"message": userDataValidation["message"]}), userDataValidation["status_code"]

        password = generate_password_hash(userData["password"])
        userData["password"] = password

        users.append(userData)
        save_file(usersFilePath)
        return jsonify({"message": f"User successfully registered."}), 201

    except Exception as e:
        return jsonify({"error": f"Error registering user: {e}"}), 500

#Login endpoint
@app.route('/login', methods=["POST"])
def log_in():
    try:
        email = request.json.get("email", None)
        password = str(request.json.get("password")) if request.json.get("password", None) else None

        if not email:
            return jsonify({"error": f"Log-in error: e-mail field is required."}), 400
        elif not password:
            return jsonify({"error": f"Log-in error: password field is required."}), 400

        for user in users:
            if user["email"] == email:
                if check_password_hash(user.get("password"), password):
                    #identity must be of type STRING. that's why we convert user["id"] to str.
                    token = create_access_token(identity=str(user["id"]))
                    return jsonify({"message": "User successfully authenticated.",
                                    "access_token": token}), 200
                else:
                    return jsonify({"error": f"Log-in error: incorrect e-mail or password."}), 401
        else:
            return jsonify({"error": f"Log-in error: unregistered e-mail."}), 401 

    except Exception as e:
        return jsonify({"error": f"Error logging user in: {e}"}), 500

#=== ENDPOINTS >>WITH<< REQUIRED JWT AUTHENTICATION ===#

#Registering a new task
@app.route('/tasks', methods=["POST"])
@jwt_required()
def register_task():
    try:
        taskData = request.get_json()

        taskDataValidation = task_data_validation(taskData)
        if type(taskDataValidation) is dict:
            return jsonify({"message": taskDataValidation["message"]}), taskDataValidation["status_code"]

        taskData["user_id"] = int(get_jwt_identity()) #since identity is of type string, we need type conversion

        tasks.append(taskData)
        save_file(tasksFilePath)

        return jsonify({"message": f"Task successfully registered."}), 201
    except Exception as e:
        return jsonify({"error": f"Error registering task: {e}"}), 500

#Getting all tasks associated to current user
@app.route('/tasks', methods=["GET"])
@jwt_required()
def get_all_tasks():
    try:
        userId = int(get_jwt_identity())

        userTasks = [task for task in tasks if task["user_id"] == userId]

        if len(userTasks) == 0:
            return jsonify({"message": "No tasks currently associated to logged in user."}), 200
        else:
            return jsonify(userTasks), 200
    except Exception as e:
        return jsonify({"error": f"Error getting all tasks: {e}"}), 500

#Getting a specific task associated to current user
@app.route('/tasks/<int:id>', methods=["GET"])
@jwt_required()
def get_specific_task(id, returnIndex=0):
    try:
        userId = int(get_jwt_identity()) #type conversion because get_jwt_identity() returns type STR.

        userTask = [task for task in tasks if task["user_id"] == userId and task["id"] == id]

        if len(userTask) == 0:
            return jsonify({"message": "No task with specified ID currently associated to current user."}), 200
        else:
            if returnIndex:
                return tasks.index(userTask)
            else:
                return jsonify(userTask[0]), 200
    except Exception as e:
        return jsonify({"error": f"Error getting task: {e}"}), 500

#Editing a specific task associated to current user
@app.route('/tasks/<int:id>', methods=["PUT"])
@jwt_required()
def edit_task(id):
    try:
        taskIndex = get_protected_task(id, int(get_jwt_identity()), returnIndex=True)
        if type(taskIndex) is dict: #means that the function either found nothing or an authorization error
            return jsonify({"message": taskIndex["message"]}), taskIndex["status_code"]

        requestJsonData = request.get_json()
        requestJsonKeys = list(requestJsonData.keys())

        #check if any of the fields in the request are mistyped or do not exist
        for key in requestJsonKeys:
            if key not in tasksRequiredFields:
                return jsonify({
                    "error": f"Field '{key}' does not exist or contains a typo. Consult the API documentation for instructions on the correct required request parameters."
                    }), 400

        #overwrite existing data with new data
        for key in requestJsonKeys:
            if key == "id":
                #this check introduces safety by not letting a user overwrite the current id with
                #another one, which could potentially result in multiple entries with the same id
                #in the system.
                continue
            tasks[taskIndex][key] = requestJsonData[key]
        
        save_file(tasksFilePath)
        return jsonify({"message": "Task successfully updated.",
                        "new_data": tasks[taskIndex]}), 200
    except Exception as e:
        return jsonify({"error": f"Error editing task: {e}"}), 500

#Deleting a specific task associated to current user
@app.route('/tasks/<int:id>', methods=["DELETE"])
@jwt_required()
def delete_task(id):
    try:
        taskIndex = get_protected_task(id, int(get_jwt_identity()), returnIndex=True)
        if type(taskIndex) is dict: #means that the function either found nothing or an authorization error
            return jsonify({"message": taskIndex["message"]}), taskIndex["status_code"]
        
        tasks.pop(taskIndex)
        save_file(tasksFilePath)
        return jsonify({"message": "Task successfully deleted."}), 200
    except Exception as e:
        return jsonify({"error": f"Error deleting task: {e}"}), 500

#=== MAIN ===#

open_file(tasksFilePath)
open_file(usersFilePath)
app.run(port=5000, host='localhost', debug=True)