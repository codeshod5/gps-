from fastapi import FastAPI,Depends,HTTPException,Query
from database import engine
from sqlmodel import Session,select
from typing import Annotated,List,Dict
from models import RouteAnArea,BusAndRoute2,Busesinfo

def get_session():
    with Session(engine) as sess:
        yield sess

app = FastAPI()
sess = Annotated[Session,Depends(get_session)]

#adding routes and areas 
@app.post('/addroutes')
def add_area_routes(routenarea: List[RouteAnArea], sess: sess):
    try:
        for i in routenarea:
            sess.add(i)
        sess.commit()
        return {"message": "Data added successfully", "count": len(routenarea)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
#if want to update area to another routeid here is update function

@app.patch('/routechange')
def update_route(sess:sess,updated:RouteAnArea):
    statement = select(RouteAnArea).where(RouteAnArea.area == updated.area)
    result = sess.exec(statement).first()
    try:

        if not result:
            raise HTTPException(status_code=404, detail="area not found")
        result.area = updated.area

        
    
        sess.add(result)
        sess.commit()
        return {'message':"updating area route_id"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
        

#add data of bus and route
@app.post('/add')
def add_to_busroute(data:List[BusAndRoute2],sess:sess):
    try:

        for i in data:
            sess.add(i)
        sess.commit()
        return {"message":"data added"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# adding businfo

@app.post('/addbusinfo')
def add_businfo(data:List[Busesinfo],sess:sess):
    try:

        for i in data:
            sess.add(i)
        sess.commit()
        return {"message":"data added"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



    
# now showing area bus and route togther 
@app.get("/info")
def show_details(sess: Session = Depends(get_session),
                 
                skip: int = Query(1,ge=1,description="page number starting from1"),
                limit: int|None = Query(10,ge=1,le=100,description="items per page (max(100))")
                 ) -> List[Dict]:
    # Step 1: Get all BusAndRoute2 entries
    try:
        ele = (skip-1)*limit
        
        statement = select(BusAndRoute2).offset(ele).limit(limit)
        results = sess.exec(statement).all()
        print("this is ress",results)

        output = []


        for entry in results:
            # print("this is entry ",entry)
            # Step 2: Get all areas for this route_id
            area_stmt = select(RouteAnArea.area).where(RouteAnArea.route_id == entry.route_id)
            areas = sess.exec(area_stmt).all()
            # print("this is areas",areas)

            # Optional: Get bus number from Busesinfo
            bus_stmt = select(Busesinfo.bus_no).where(Busesinfo.bus_id == entry.bus_id)
            
            bus_no = sess.exec(bus_stmt).first()
            # print("this isbus_stmt",bus_no)


            output.append({
                "route_id": entry.route_id,
                "areas": areas,
                "bus_id": entry.bus_id,
                "bus_no": bus_no,  # Optional
                "timming": entry.timming
            })

        return output
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
        




    


        
    


    




    
    

    

