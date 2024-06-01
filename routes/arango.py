
from bottle import get, post, delete, put, request
from icecream import ic
from arango_util import arango


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
        q = {"query":"FOR e IN employees FILTER e.employee_name == @name RETURN e","bindVars":{"name":name}}
        employee = arango(q)
        return employee
    except Exception as ex:
        ic(ex)
        return ex
    finally:
        pass


##############################


@post("/arango/employees")
def _():
    try:
       #TODO: validate
        employe_name = request.forms.get("employe_name","")
        employe_email= request.forms.get("employe_email","")

        employee={"employee_name": employe_name,
                  "employee_email":employe_email,
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
        return ex
    finally:
        pass


##############################

@put("/arango/employees/<key>")
def _(key):
    try:
        employe_email= request.forms.get("employe_email","")

        employee={
                  "employee_email":employe_email,
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
        return ex
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
        return ex
    finally:
        pass
