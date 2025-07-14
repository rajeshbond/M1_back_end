from operator import mod
from pyexpat import model
from app import oauth2
from .. import models, schemas,oauth2# importing models schemase , utls 
from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from ..database import get_db
from typing import List, Optional
from sqlalchemy import func

router = APIRouter(
    prefix= "/posts",
    tags=["Post"]
)


    
    
# @router.get("/",response_model=List[schemas.Post])
@router.get("/",response_model= List[schemas.PostOut])
def get_posts(db: Session = Depends(get_db),current_user: int = Depends(oauth2.get_current_user),
             limit: int = 10,
             skip: int = 0,
             search: Optional[str] = ""):
    # posts_query = db.query(models.Post).filter(models.Post.owner_id == current_user.id) # to use for user_Id spedific 
    # # posts_query = db.query(models.Post)
    # post = posts_query.filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    post_query = db.query(models.Post, func.count(models.Votes.post_id).label("votes")).join(models.Votes,
                                                                                  models.Votes.post_id == models.Post.id,
                                                                                  isouter = True).group_by(models.Post.id)
    post =  post_query.filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
 
    return post

    
    # cursor.execute(""" SELECT * FROM posts """)
    # posts = cursor.fetchall()
    # print(posts) 
    # def create_posts(payLoad: dict = Body(...)): # the body data converted to the dict format 
#     print(payLoad)
#     return{"new_post":f"title:{payLoad['title']} content:{payLoad['content']}"}
#=====================================the def end here =============================================

    
    
    
# --------------------------The function decleration ------------------------------
# the data get validated from the pydentic BaseMold Schema for error proofing 
   

@router.post("/", status_code= status.HTTP_201_CREATED,response_model= schemas.Post)

def create_post(post: schemas.PostCreate, db: Session = Depends(get_db),
                current_user: int = Depends(oauth2.get_current_user)): 
 
    print(current_user.id) # This is only for debugging purpose 
    new_post = models.Post(owner_id = current_user.id,**post.dict())
                    # title=post.title,
                    # content=post.content,
                    # publish=post.publish)
    
    db.add(new_post)  # need to add the post 
    db.commit() # need to push the entry to the database 
    db.refresh(new_post) # we need to retun the data base by refreshing the file 
    # print(new_post.title,new_post.content])
    return new_post
  # -------------------------- The old code without database ----------------------------#
    # print(f"{new_post.title} and {new_post.content} {new_post.publish} {new_post.rating}") # its very easy to extract the value directly from the key ref.
    # The data send is in Pydantic model and can be converted to other data models like dict as pe the below example
    # print(post.dict())
    # post_dict = post.dict()
    # post_dict['id'] = randrange(0,100000)
    # my_post.append(post_dict) 
    # print(f'Hello {post_dict}')
    # return{"data":post_dict}
# ==================================================================================================
# @router.get("/posts/latest")
# def get_latest_post(   ):
#     post = my_post[len(my_post)-1]
#     return post

# =============The fucntion starts here ============================================================
@router.get("/{id}", status_code= status.HTTP_201_CREATED, response_model= schemas.PostOut)
def get_post(id: int, response: Response,db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
 
    # post_quirey = db.query(models.Post).filter(models.Post.id == id)
    # post = post_quirey.first()
    post_query = db.query(models.Post, func.count(models.Votes.post_id).label("votes")).join(models.Votes,
                                                                                  models.Votes.post_id == models.Post.id,
                                                                                  isouter = True).group_by(models.Post.id)
    post = post_query.filter(models.Post.id == id).first()
   
    if not post:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail=f"No Post avalable for ID {id}") # This HttP method we will use the most 
    # if current_user.id != post.owner_id: # if you want to go specifc with user id 
    #     raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, detail= f'you are not Authoriesed ')

    return post

# post = find_post(id)
    # print(f"The Id passed is :- {str(id)} *****")
    # cursor.execute(""" SELECT * FROM posts WHERE id = %s """ , (str(id),)) # , need to be provided after str(id) if not it will not operate after 9 
    # test_post = cursor.fetchone()
    # print(test_post)   
    # Below method are lenthlty and not much effective
    # response.status_code = status.HTTP_404_NOT_FOUND
    # return{"message":f"No Post avalable for ID {id} "}
    
# ==================================================================================
    
      
 

@router.put("/{id}",response_model= schemas.Post)
def update_post(id: int, post: schemas.PostCreate, db: Session = Depends(get_db),current_user: int = Depends(oauth2.get_current_user)): # for updating the field all the fields required as per pydentic model ll
    # index = find_index_post(id) 
    # cursor.execute("""UPDATE posts SET title = %s, content = %s, publish =%s WHERE id = %s RETURNING * """, # dont put , befor RETURNING
    #                (post.title, post.content,post.publish, str(id),))
    # updated_post = cursor.fetchone()
    # conn.commit()
    updated_post_query = db.query(models.Post).filter(models.Post.id == id)
    updated_post = updated_post_query.first()
    
    if updated_post == None: # checking for the id in the database if none then through the Http Error
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,detail= f"No Post avalable for ID {id}")
    if(current_user.id != updated_post.owner_id):
            raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, detail= f"Not Authorized to perforn requested action")
     
    
    updated_post_query.update(post.dict(), synchronize_session=False)
    
    db.commit()
    updated_post = updated_post_query.first()
   
    print(update_post)
    # post_dict = post.dict() # converting the incoming post to dict
    # post_dict['id'] = id # This code is assigning the request id to the dict ( so this is important to use )
    # my_post[index] = post_dict
    # print(my_post)
    return updated_post 

# ===========================================================================================

@router.delete("/{id}", status_code= status.HTTP_201_CREATED)
def delete_post(id: int, response: Response,db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if not post:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail=f"No Post avalable for ID {id}") # This HttP method we will use the most 
    if(current_user.id != post.owner_id):
            raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, detail= f"Not Authorized to perform requested action")
    pos = post
    
    post_query.delete(synchronize_session=False)
    db.commit()
    return {"Respose": Response(status_code=status.HTTP_204_NO_CONTENT)} 
    

   
# @router.delete("/{id}") #status_code= status.HTTP_204_NO_CONTENT)
# def delete_post(id: int,post: schemas.Post,response: Response,db: Session = Depends(get_db),
#                 current_user: int = Depends(oauth2.get_current_user)):
#     print(id)
    
#     post = db.query(models.Post).filter(models.Post.id == id)
  
    
#     if post.first() == None: # checking for the id in the database if none then through the Http Error
#         raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,detail= f"No Post avalable for ID {id}")

#     post.delete(synchronize_session=False)
#     db.commit()
#     return {"Respose": Response(status_code=status.HTTP_204_NO_CONTENT ) } 

  
    # print(post.owner_id)
    
    # if post.owner_id != oauth2.get_current_user.id:
    #     print("Hello")
  
    
    # # index = find_index_post(id) 
    # cursor.execute(""" DELETE FROM posts WHERE id = %s RETURNING * """ , (str(id),))
    # deleted_post = cursor.fetchone()
    # print(f"***************Post deletd {deleted_post}*************")
    # conn.commit()
    # if deleted_post == None: # checking for the id in the database if none then through the Http Error
    #     raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,detail= f"No Post avalable for ID {id}")
    # # else:
    #     raise HTTPException(status_code= status.HTTP_204_NO_CONTENT,detail= f"  Post deleted for  {id}")
    # my_post.pop(deleted_post) The is being now directly taken care by PostGress Quirey now no need to use pop j
    # return Response(status_code=status.HTTP_204_NO_CONTENT),  # sending resposnse to coder 


