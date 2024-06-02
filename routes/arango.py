import re
from bottle import get, post, delete, put, request, response
from icecream import ic
from arango_util import arango
from utility.regexes import USER_FIRST_NAME_REGEX, USER_LAST_NAME_REGEX, USER_EMAIL_REGEX
from utility.utils import validate_email


def validate_full_name(full_name):
    first_name, last_name = full_name.split(" ")
    if re.match(USER_FIRST_NAME_REGEX, first_name) and re.match(USER_LAST_NAME_REGEX, last_name):
        return full_name
    else:
        raise Exception(f"{full_name} is not a valid full name", 400)


@get("/arango/employees")
def _():
    try:
        q = {"query":"FOR e IN employees RETURN e"}
        emplpyees = arango(q)
        return emplpyees
    except Exception as ex:
        ic(ex)
        return ex
    finally:
        pass

##############################

@get("/arango/employees/name")
def _():
    try:
        name = request.query.get("name","")
        full_name = validate_full_name(name)
        q = {
            "query":"FOR e IN employees FILTER e.employee_name == @name RETURN e",
            "bindVars":{"name":full_name},
        }
        employee = arango(q)
        return employee
    except Exception as ex:
        ic(ex)
        response.status = 400
        return "input error"
    finally:
        pass


##############################


@post("/arango/employees")
def _():
    try:
        full_name = validate_full_name(request.forms.get("user_full_name"))
        email = validate_email()
        employee={"employee_name": full_name,
                  "employee_email":email,
                  "leader": {
	                    "leader_id": None,
	                    "leader_name": None,
                        },
                        "projects": []
                  }
        q={"query":"INSERT @employee INTO employees RETURN NEW", "bindVars":{"employee":employee}}
        employee = arango(q)
        return employee
    except Exception as ex:
        ic(ex)
        response.status = 400
        return "input error"
    finally:
        pass


##############################

@put("/arango/employees/<key>")
def _(key):
    try:
        email = validate_email()
        employee={
                  "employee_email":email,
                  "version":2
                  }
        employee_key={"_key": key}
        q = {"query":"UPDATE @employee_key WITH @employee in employees RETURN NEW", 
             "bindVars":{"employee_key":employee_key,
                         "employee":employee}
             }
        employee = arango(q)
        return employee
    except Exception as ex:
        ic(ex)
        response.status = 400
        return "input error"
    finally:
        pass
       

##############################

@delete("/arango/employees/<key>")
def _(key):
    try:
        key={"_key": key}
        q = {"query":"REMOVE @key IN employees RETURN OLD", 
             "bindVars":{"key":key}
             }
        employee = arango(q)
        return employee
    except Exception as ex:
        ic(ex)
        response.status = 400
        return "invalid key"
    finally:
        pass
