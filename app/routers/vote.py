from fastapi import Response, status, HTTPException, Depends, APIRouter
from .. import models, schemas,oauth2, database
from sqlalchemy.orm import Session


router = APIRouter(
    prefix= '/vote',
     tags=["Votes"]
)

@router.post("/",status_code= status.HTTP_201_CREATED)
def vote(vote: schemas.Vote,
        db: Session = Depends(database.get_db),
        current_user: int = Depends(oauth2.get_current_user)):
    
    post_query = db.query(models.Post).filter(models.Post.id == vote.post_id)
    post = post_query.first()
    
    if not post:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,detail= f"The post with id {vote.post_id} do not exist")
    
    vote_query = db.query(models.Votes).filter(models.Votes.post_id == vote.post_id, 
                                  models.Votes.user_id == current_user.id)
    found_vote = vote_query.first()
    #  vote condition logic 
    if (vote.dir == 1):
        if found_vote:
            raise HTTPException(status_code= status.HTTP_409_CONFLICT,
                                detail= f"user {current_user.id} has already voted on the post {vote.post_id}")
        new_vote = models.Votes(post_id = vote.post_id,
                     user_id = current_user.id)
        db.add(new_vote)
        db.commit()
        return{"message": "addded vote sucessfully" }
    else:
        if not found_vote:
            raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,detail= " no Vote found ")
        vote_query.delete(synchronize_session=False)
        db.commit()
        return{"message": "deleted vote sucessfully" }