
from .. import models, schemas, utls # importing models schemase , utls #added
from fastapi import Response, status, HTTPException, Depends, APIRouter #added 
from sqlalchemy.orm import Session #added 
from ..database import get_db #added
from ..import database, schemas, models,utls, oauth2 # added new
import uuid # added new
from sqlalchemy.orm import sessionmaker # added new
from sqlalchemy.sql.expression import text # added new
from sqlalchemy.sql import alias, select,case  
from sqlalchemy.sql import expression  # added new
import smtplib # new added
import random

MY_EMAIL = "noreply.sntsoulutions.in@gmail.com"
MY_PASSWORD = "rnphucprkrpeuvic"  # APP password with 2 factor authentication 







router = APIRouter(
    prefix= '/users',
     tags=["Users"]
)


#-------------------------------------- Fresh New User Creation code starts Here ----------------------------------

@router.post("/", status_code= status.HTTP_201_CREATED, response_model=schemas.UserOut)

def create_users(user: schemas.UserCreate, db: Session = Depends(get_db)): 
    
    # Hash the password - user.password 
    print(user.password)
    hased_password = utls.hash(user.password)
    user.password = hased_password  
    already_user_query = db.query(models.User).filter(models.User.email == user.email)
    if already_user_query.first():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail= f"{user.email} already exit")
  
    new_user = models.User(**user.dict())
    db.add(new_user)  # need to add the post 
    # db.commit()  
    # db.refresh(new_user) # we need to retun the data base by refreshing the file 
    reset_code1 = str(uuid.uuid1())
 
    
    c1 = models.codes1(
                         email=user.email,
                         reset_code=reset_code1,
                        ) 
    db.add(c1)
    # db.commit()
  
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as mail_connection:
                        mail_connection.starttls()
                        print(f"To {c1.email} From {MY_EMAIL}")
                        mail_connection.login(user= MY_EMAIL,password =MY_PASSWORD)
                        mail_connection.sendmail(
                                from_addr=MY_EMAIL,
                                to_addrs=c1.email,
                                msg=f"Subject: Account Verifcation  \n\n Hello {user.name.title()},\n http://127.0.0.1:8000/users/verify/{c1.reset_code}\n from \n SNT Solutions"
                        )
        db.commit()
        db.refresh(new_user)
        return new_user
        
       
    except :
        raise HTTPException(status_code= status.HTTP_502_BAD_GATEWAY, detail= "look like you are offline , check internet connections")
        

        
        
   
     
    

#-------------USER CREATION ENDS HERE --------------------------------------------------
  
###########################Search user by ID ######################################

@router.get('/{id}',response_model=schemas.UserOut)
def get_user(id: int,db: Session = Depends(get_db)):
    user_query = db.query(models.User).filter(models.User.id == id)
    user = user_query.first()
    if not user:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail=f"No Post avalable for ID {id}") 
    
    return user

#--------------------Search user by ID--------------------------------------------------


############################# Reset password #############################################
@router.patch("/changepwd",status_code=status.HTTP_202_ACCEPTED,response_model= schemas.UserOut)
def password_rest(user:schemas.UserChangePassword, db: Session = Depends(get_db),current_user: int = Depends(oauth2.get_current_user) ):
    
    if not utls.verify(user.password, current_user.password):
            print(user.password)
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail= "Invalid Credentials")
       
    hased_password = utls.hash(user.password_new)
    user.password = hased_password
    current_user.password = user.password
    db.commit()
    return current_user    

#--------------------forgot password --------------------------------------------------


@router.post("/forgotpassword")

async def forgot_password(user:schemas.ForgotPassword,db: Session = Depends(get_db)):
    # check user existed 
    
    user1_query = db.query(models.User).filter(models.User.email== user.email.lower()) # user is users table class name
    user1 = user1_query.first()
    if not user:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= " please porvide valid email id" ) 
    
  
    # reset_code1 = str(uuid.uuid1()) 
    reset_code1 = random.randrange(111111, 999999, 6)
    
 
    
    c1 = models.codes1(
                         email=user.email,
                         reset_code=reset_code1,
                        ) 
    db.add(c1)
    db.commit()
    print(c1.email,c1.reset_code)

    with smtplib.SMTP("smtp.gmail.com", 587) as mail_connection:
        mail_connection.starttls()
        print(f"To {c1.email} From {MY_EMAIL}")
        mail_connection.login(user= MY_EMAIL,password =MY_PASSWORD)
       
        mail_connection.sendmail(
            from_addr=MY_EMAIL,
            to_addrs={c1.email},
            # msg=f"Subject:Forget password link   \n\n Hello {user1.name},\n http://127.0.0.1:8000/users/forgetlink/{c1.reset_code} \n from \n SNT Solutions")
            msg=f"Subject:Forget password OTP  \n\n Hello {user1.name},\n your OTP to rest password is  \n\n    {c1.reset_code} \n\n  from \n SNT Solutions")
   
     
    return {"messgae":"sucessful"}
   
#  user verifvation code 
@router.get("/verify/{reset_code1}")
def user_verify(reset_code1: str, db: Session = Depends(get_db)):
    verify_query_code = db.query(models.codes1).filter(models.codes1.reset_code == reset_code1)
    print(verify_query_code)
    verify_code = verify_query_code.first()
    print(verify_code.email)
    
    user_query = db.query(models.User).filter(models.User.email == verify_code.email)
    user = user_query.first()
    print(user.email)
    if user:
        
        user.is_verified_user = True
        db.commit()  
        
    
    return f"User {user.name} verifed sucessfully "

#  forget link set password 

@router.patch("/forgetlink/",status_code= status.HTTP_201_CREATED)
def user_verify(user:schemas.ForgotPasswordChange , db: Session = Depends(get_db)):
    print(user.reset_code1)
    verify_user_queiry = db.query(models.codes1).filter(models.codes1.reset_code == user.reset_code1)
    # verify_user = verify_user_queiry.first()
    verify_user = verify_user_queiry.order_by(models.codes1.id.desc()).first()
    user1_query = db.query(models.User).filter(models.User.email == verify_user.email)
    user1 = user1_query.first()
    print(user1.email)
    if user1:
       
        hased_password = utls.hash(user.password)
        user1.password = hased_password  
        db.commit()        
    
    return f"User {user1.email} password change succesfully  "

    

















