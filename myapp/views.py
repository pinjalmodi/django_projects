from django.shortcuts import render,redirect,get_object_or_404
from .models import User,Contact,RegistrationRequest,Notice,Member,PaymentOrder,Image
import random
from django.core.mail import send_mail
from django.conf import settings
import datetime
from django.db.models import DecimalField
from decimal import Decimal
from django.contrib import messages
from django.db.models import F
import requests
import razorpay
from .models import PaymentOrder
import logging
from django.http import HttpResponse,JsonResponse
import json

# Create your views here.

def index(request):
	return render(request,'index.html')

def admin_index(request):
	try:
		user=User.objects.get(email=request.session['email'])
		if user.usertype=='admin':
			reg_users=User.objects.all().order_by("-id")[:3]
			orders=PaymentOrder.objects.all().order_by('-id')[:4]

			return render(request,'admin-index.html',{'reg_users':reg_users,'orders':orders})
		else:
			return render(request,'member-index.html',{'reg_users':reg_users,'orders':orders})
	except:
		return render(request,'index.html')

def member_index(request):
	try:
		user=User.objects.get(email=request.session['email'])
		if user.usertype=='member':
			reg_users=User.objects.all().order_by("-id")[:3]
			orders=PaymentOrder.objects.all().order_by('-id')[:4]

			return render(request,'member-index.html',{'reg_users':reg_users,'orders':orders})
		else:
			return render(request,'admin-index.html',{'reg_users':reg_users,'orders':orders})
	except:
		return render(request,'index.html')


def contact(request):
	if request.method=="POST":
		Contact.objects.create(
			name=request.POST['name'],
			email=request.POST['email'],
			mobile=request.POST['mobile'],
			remarks=request.POST['remarks']

			)
		msg="Contact Saved Successfully"
		return render(request,'contact.html',{'msg':msg})
	else:
		return render(request,'contact.html')

def register(request):
	if request.method=="POST":
		try:
			user=User.objects.get(email=request.POST['email'])
			msg="Email Already Registered"
			return render(request,'register.html',{'msg': msg})
		except:
			if request.POST['password']==request.POST['cpassword']:
				user=User.objects.create(
					usertype=request.POST['usertype'],
					bunglow_no=request.POST['bunglow_no'],
					fname=request.POST['f_name'],
					lname=request.POST['l_name'],
					email=request.POST['email'],
					mobile=request.POST['mobile'],
					address=request.POST['address'],
					password=request.POST['password'],
					profile_picture=request.FILES['profile_picture'],
				)


				RegistrationRequest.objects.create(user=user,email=user.email,status='Pending')

				request.session['email']=user.email
				msg="Your registration request is pending."
				return render(request,'register.html',{'msg':msg})	

			else:
				msg="Password and Confirm Password Does Not Match"
				return render(request,'register.html',{'msg':msg})

	else:
		return render(request,'register.html')


def login(request):
	if request.method=="POST":
		try:
			user=User.objects.get(email=request.POST['email'])
			if user.password==request.POST['password']:
				if user.status=="approved":
					request.session['email']=user.email
					request.session['fname']=user.fname
					request.session['profile_picture']=user.profile_picture.url
					due_amount = user.due_amount
					request.session['due_amount'] = float(due_amount) if due_amount is not None else 0.0
					msg="Login Successful"
					if user.usertype == 'admin':
						return redirect('admin-index')
					else:
						msg="Login Successful"
						return redirect('member-index')	
				else:
					msg="Your status is not approved yet"
					return render(request,'login.html',{'msg':msg})

			else:
				msg="Password Incorrect"
				return render(request,'login.html',{'msg':msg})
		except:
			msg="Email Not Registered"
			return render(request,'register.html',{'msg':msg})
	else:
		return render(request,'login.html')

def logout(request):
	try:
		del request.session['email']
		del request.session['fname']
		del request.session['profile_picture']
		msg="Logged Out Successfully"
		return render(request,'login.html',{'msg':msg})


	except:
		msg="Logged Out Successfully"
		return render(request,'login.html',{'msg':msg})

def forgot_password(request):
	if request.method=="POST":
		try:
			user=User.objects.get(email=request.POST['email'])
			otp=str(random.randint(1000,9999))
			subject = 'OTP for Forgot Password'
			message = 'Hello'+user.fname+'Your OTP for forgot Password is'+str(otp)
			email_from = settings.EMAIL_HOST_USER
			recipient_list = [user.email, ]
			send_mail( subject, message, email_from, recipient_list )
			request.session['email']=user.email
			request.session['otp']=otp
			if user.usertype == 'admin':
				return render(request,'admin-otp.html')
			else:
				return render(request,'member-otp.html')
			
		except:
			msg='Email id Not Registered'
			return render(request,'register.html',{'msg': msg})

	else:
		return render(request,'forgot-password.html')

def verify_otp(request):
	otp1=int(request.POST['otp'])
	otp2=int(request.session['otp'])
	if otp1==otp2:
		del request.session['otp']
		if user.usertype == 'admin':
			return render(request,'admin-new-password.html')
		else:
			return render(request,'member-new-password.html')
			

	else:
		msg='Invalid OTP'
		return render(request,'otp.html',{'msg':msg})

def new_password(request):
	if request.POST['new_password']==request.POST['cnew_password']:
		user=User.objects.get(email=request.session['email'])
		if user.password!=request.POST['new_password']:
			user.password=request.POST['new_password']
			user.save()
			del request.session['email']
			msg="Password Updated Successfully"
			return render(request,'login.html',{'msg':msg})
		else:
			msg='New password cannot be from old passwords'
			if user.usertype == 'admin':
				return render(request,'admin-new-password.html',{'msg':msg})
			else:
				return render(request,'member-new-password.html',{'msg':msg})
			
			
	else:
		msg="New password and confirm new password does not match"
		if user.usertype == 'admin':
			return render(request,'admin-new-password.html',{'msg':msg})
		else:
			return render(request,'member-new-password.html',{'msg':msg})
				
	
def make_requests(request):
	pending_users=RegistrationRequest.objects.all()
	return render(request,'make-requests.html',{'pending_users':pending_users})

def approve_user(request,user_id):
	pending_user = get_object_or_404(RegistrationRequest, id=user_id)
	send_mail('Congratulations!', 'You can now log in.', None, [pending_user.email])
	pending_user.delete()
	status='approved'
	messages.success(request, 'User approved successfully.')
	return redirect('make-requests')

def decline_user(request, user_id):
    pending_user = get_object_or_404(RegistrationRequest, id=user_id)
    user = pending_user.user
    pending_user.delete()
    user.delete()
    messages.success(request, 'User declined successfully.')
    return redirect('make-requests')

    
def profile(request):
	user=User.objects.get(email=request.session['email'])
	if request.method=="POST":
		user.fname=request.POST['f_name']
		user.lname=request.POST['l_name']
		user.mobile=request.POST['mobile']
		user.address=request.POST['address']
		try:
			user.profile_picture=request.FILES['profile_picture']
		except:
			pass
		user.save()
		request.session['profile_picture']=user.profile_picture.url


		msg='Profile Updated Succesfully'
		if user.usertype == 'admin':
			return render(request,'admin-profile.html',{'user':user,'msg':msg})
		else:
			return render(request,'profile.html',{'user':user,'msg':msg})
	else:	
		return render(request,'profile.html',{'user':user})

def admin_profile(request):
	user=User.objects.get(email=request.session['email'])
	if request.method=="POST":
		user.fname=request.POST['f_name']
		user.lname=request.POST['l_name']
		user.mobile=request.POST['mobile']
		user.address=request.POST['address']
		try:
			user.profile_picture=request.FILES['profile_picture']
		except:
			pass
		user.save()
		request.session['profile_picture']=user.profile_picture.url


		msg='Profile Updated Succesfully'
		if user.usertype == 'admin':
			return render(request,'admin-profile.html',{'user':user,'msg':msg})
		else:
			return render(request,'profile.html',{'user':user,'msg':msg})
	else:	
		return render(request,'admin-profile.html',{'user':user})


def change_password(request):
	user=User.objects.get(email=request.session['email'])
	if request.method=="POST":
		if user.password==request.POST['old_password']:
			if user.password!=request.POST['new_password']:
				if request.POST['new_password']==request.POST['cnew_password']:
					user.password=request.POST['new_password']
					user.save()
					del request.session['email']
					del request.session['fname']
					msg="Password Updates Successfully"

					return render(request,'login.html',{'msg': msg})

				else:
					msg='New Password and confirm new Password does not match'
					if user.usertype == 'admin':
						return render(request,'admin-change-password.html',{'msg':msg})
					else:
						return render(request,'member-change-password.html',{'msg':msg})
					

			else:
				msg='New Password cannot be from old passwords'
				if user.usertype == 'admin':
					return render(request,'admin-change-password.html',{'msg':msg})
				else:
					return render(request,'member-change-password.html',{'msg':msg})
					
			
		else:
			msg="Incorrect old Password"
			if user.usertype == 'admin':
				return render(request,'admin-change-password.html',{'msg':msg})
			else:
				return render(request,'member-change-password.html',{'msg':msg})
	else:
		return render(request,'change-password.html')

def admin_change_password(request):
	user=User.objects.get(email=request.session['email'])
	if request.method=="POST":
		if user.password==request.POST['old_password']:
			if user.password!=request.POST['new_password']:
				if request.POST['new_password']==request.POST['cnew_password']:
					user.password=request.POST['new_password']
					user.save()
					del request.session['email']
					del request.session['fname']
					msg="Password Updates Successfully"

					return render(request,'login.html',{'msg': msg})

				else:
					msg='New Password and confirm new Password does not match'
					if user.usertype == 'admin':
						return render(request,'admin-change-password.html',{'msg':msg})
					else:
						return render(request,'member-change-password.html',{'msg':msg})
					

			else:
				msg='New Password cannot be from old passwords'
				if user.usertype == 'admin':
					return render(request,'admin-change-password.html',{'msg':msg})
				else:
					return render(request,'member-change-password.html',{'msg':msg})
					
			
		else:
			msg="Incorrect old Password"
			if user.usertype == 'admin':
				return render(request,'admin-change-password.html',{'msg':msg})
			else:
				return render(request,'member-change-password.html',{'msg':msg})
	else:
		return render(request,'admin-change-password.html')

def admin_member_information(request):
	if request.method=="POST":
		action = request.POST.get('action')
		if action=='add':
			User.objects.create(
				usertype=request.POST['usertype'],
				bunglow_no=request.POST['bunglow_no'],
				fname=request.POST['f_name'],
				lname=request.POST['l_name'],
				email=request.POST['email'],				
				mobile=request.POST['mobile'],
				address=request.POST['address'],
				password=request.POST['password'],
				profile_picture=request.FILES['profile_picture']
				)

			msg="User added successfully"

			return render(request,'admin-member-information.html',{'msg':msg})

		elif action=='update':
			email = request.POST.get('email')
			try:
				user=User.objects.get(email=email)
				
		
				user.usertype=request.POST.get('usertype')
				user.bunglow_no=request.POST.get('bunglow_no')
				user.fname=request.POST.get('f_name')
				user.lname=request.POST.get('l_name')			
				user.mobile=request.POST.get('mobile')
				user.address=request.POST.get('address')
				user.password=request.POST.get('password')
				if 'profile_picture' in request.FILES:
					user.profile_picture=request.FILES['profile_picture']
				user.save()
				msg="User Updated successfully"
				return render(request,'admin-member-information.html',{'msg':msg})
			except User.DoesNotExist:
				msg='User Not Found'
				return render(request,'admin-member-information.html',{'msg':msg})


		elif action=='delete':
			email = request.POST.get('email')
			try:
				user=User.objects.get(email=email)
				user.delete()
				msg="User deleted successfully"
				return render(request,'admin-member-information.html',{'msg':msg})
			except:
				msg="User Not Found"
				return render(request,'admin-member-information.html',{'msg':msg})


		else:
			msg='Invalid Action'
			return render(request,'admin-member-information.html',{'msg':msg})
	else:
		return render(request,'admin-member-information.html')

def admin_maintenance(request):
	user=User.objects.get(email=request.session['email'])
	users=User.objects.all()
	due_amount = request.session.get('due_amount')
	if user.usertype=='admin':
		return render(request, 'admin-maintenance.html',{'users':users,'due_amount':due_amount})
	else:
		return render(request, 'member-maintenance.html',{'users':users,'due_amount':due_amount})


def admin_member_information_view(request):
	user=User.objects.get(email=request.session['email'])

	users=User.objects.all()
	if user.usertype == 'admin':
		return render(request,'admin-member-information-view.html',{'users': users})
	else:
		return render(request,'member-member-information-view.html',{'users': users})
	
def notices(request):
	if request.method=="POST":
		action = request.POST.get('action')
		if action=='add':
			Notice.objects.create(
				title=request.POST['title'],
				notice=request.POST['notice']
				)
			
			msg="Notice added successfully"

			
		elif action=='update':
			title=request.POST.get('title')
			new_notice_content = request.POST.get('notice')

			try:
				notice = Notice.objects.get(title=title)
				notice.notice = new_notice_content
				notice.save()
				msg='Notice Updated Succesfully'

				
			except Notice.DoesNotExist:
				msg="Notice Not Found"
				


		elif action=='delete':
			title=request.POST.get('title')
			try:
				notice = Notice.objects.get(title=title)
				notice.delete()
				msg="Notice deleted successfully"
				
			except Notice.DoesNotExist:
				msg="Notice Not Found"
				



		else:
			msg='Invalid Action'
		return render(request,'notices.html',{'msg':msg})
	else:
		return render(request,'notices.html')

def member_notices(request):
	user=User.objects.get(email=request.session['email'])
	notices=Notice.objects.all().order_by('-id')[:2]
	if user.usertype=='admin':
		return render(request,'admin-notices.html',{'notices':notices})
	else:
		return render(request,'member-notices.html',{'notices':notices})
"""
def admin_maintenance(request):
	
	users=User.objects.all()
	
	members=Member.objects.all()
	return render(request,'admin-maintenance.html',{'users':users})
"""

def add_maintenance(request):
    if request.method == "POST":
        action = request.POST.get('action')
        
        if action == 'add':
            try:
                # Convert maintenance to Decimal
                maintenance = Decimal(request.POST.get('maintenance', '0.00'))
                
                # Validate maintenance value
                if maintenance <= 0:
                    messages.error(request, 'Invalid Maintenance Amount.')
                    return render(request, 'add-maintenance.html')
                
                # Update due_amount for all Member objects
                users = User.objects.all()
                for i in users:
                    try:
                        i.due_amount += maintenance
                        i.save()
                    except Exception as e:
                        messages.error(request, 'Error updating member: {}'.format(e))
                        return render(request, 'add-maintenance.html')
                
                messages.success(request, 'Maintenance amount added successfully.')
            except (ValueError, InvalidOperation):
                messages.error(request, 'Incorrect Amount.')
        else:
            messages.error(request, 'Invalid Action.')
    
    # Ensure the view always returns an HttpResponse
    return render(request, 'add-maintenance.html')

def Discussion_List(request):
    url = "http://localhost:8001/myapp/discussion"  # Adjust the URL if needed
    if request.method == "POST":    
        querystring = {
            "title": request.POST.get('title'),
            "content": request.POST.get('content'),
            "created_at": request.POST.get('created_at'),  # If not needed, remove this
            "author": request.POST.get('author'),
        }

        response = requests.post(url, json=querystring)
        print(response)
        msg="s" if response.status_code == 201 else "Failed to create discussion."

        return render(request, 'discussionlist.html', {"msg": msg})

    else:
        response = requests.get(url)
        discussions = response.json() if response.status_code == 200 else []
        print(discussions)
        return render(request, 'discussionlist.html', {"discussions": discussions})



def discussion_detail(request, discussion_id):
	user=User.objects.get(email=request.session['email'])
	API_url = f"http://localhost:8001/myapp/discussion/{discussion_id}"
	discussion_response = requests.get(API_url)
	if discussion_response.status_code == 200:
	    discussion = discussion_response.json()
	else:
	    discussion = None
	comments_url = f"http://localhost:8001/myapp/comment?discussion={discussion_id}"
	comments_response = requests.get(comments_url)
	if comments_response.status_code == 200:
	    comments=[comment for comment in comments_response.json() if comment['discussion'] == discussion_id]
	else:
		comments=[]
	if request.method == "POST":
		querystring = {"discussion": discussion_id,"content": request.POST.get('content'),"author": request.POST.get('author')}
		url = "http://localhost:8001/myapp/comment"
		response = requests.post(url, json=querystring)
		msg='Comment added successfully'
		if user.usertype=='admin':
			return render(request, 'admin-discussion-detail.html', {"msg": msg, "discussion": discussion, 'discussion_id':discussion_id,'comments':comments})
		else:
			return render(request, 'member-discussion-detail.html', {"msg": msg, "discussion": discussion, 'discussion_id':discussion_id,'comments':comments})
	return render(request, 'discussion-detail.html', {"discussion": discussion, 'discussion_id': discussion_id,'comments':comments})


"""
        if response.status_code in [200,201]:
        	
        else:
        	msg = f"Failed to add comment: {response.content.decode()}"  # Show server response
"""		
		
		

logger = logging.getLogger(__name__)

def create_order(request):
    client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))

    user = User.objects.get(email=request.session['email'])
    due_amount = request.session.get('due_amount', 0.0)

    if request.method == 'POST':
        amount_str = request.POST.get('amount')

        if not amount_str or amount_str.strip() == "":
            logger.error("Amount not found in request.")
            return render(request, 'create_order.html', {
                'error': "Amount not found in request.",
                'due_amount': due_amount
            })

        try:
            amount = Decimal(amount_str)

            if amount <= 0:
                raise ValueError("Amount must be greater than zero.")

            order = client.order.create({
                'amount': int(amount * 100),
                'currency': 'INR',
                'payment_capture': '1'
            })

            payment_order = PaymentOrder(order_id=order['id'], amount=amount, currency='INR')
            payment_order.save()
            

            logger.info("Order created successfully: %s", order['id'])

            context = {
                'order_id': order['id'],
                'amount': int(amount * 100),
                'due_amount': due_amount,
            }
            if user.usertype=='admin':
            	return render(request, 'admin-payment.html',context)
            else:
            	return render(request, 'member-payment.html',context)

           

        except Exception as e:
            logger.error("Error creating order: %s", str(e))
            return render(request, 'create_order.html', {
                'error': "Failed to create order. Please try again.",
                'due_amount': due_amount
            })

    if user.usertype=='admin':
    	return render(request, 'create_order.html', {'due_amount': due_amount})
    else:
    	return render(request, 'member-create-order.html', {'due_amount': due_amount})



    

def payment(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  # Parse JSON request body
            order_id = data.get('order_id')
            payment_id = data.get('payment_id')
            amount=data.get('amount')

            if not order_id:
                logger.error("Order ID not provided.")
                return JsonResponse({'success': False, 'error': 'Order ID is required.'})

            # Proceed with your payment confirmation logic...
            order = PaymentOrder.objects.get(order_id=order_id)
            payment_success, error_message = confirm_payment(order)

            if payment_success:
                logger.info(f"Payment successful for order ID: {order_id}")
                return JsonResponse({'success': True, 'message': 'Payment successful!'})
            else:
                logger.error(f"Payment failed for order ID: {order_id} - {error_message}")
                return JsonResponse({'success': False, 'error': error_message})

        except json.JSONDecodeError:
            logger.error("Invalid JSON received.")
            return JsonResponse({'success': False, 'error': 'Invalid JSON received.'})
        except Exception as e:
            logger.error(f"Unexpected error occurred: {str(e)}")
            return JsonResponse({'success': False, 'error': 'An unexpected error occurred.'})

    logger.warning('Invalid request method: Only POST requests are allowed.')
    return JsonResponse({'success': False, 'error': 'Invalid request method. Please use POST.'})

def payment_all(request):
	user=User.objects.get(email=request.session['email'])
	if request.method == 'POST':
	    order_id = request.POST.get('order_id')
	    pass
	else:
	    orders = PaymentOrder.objects.all()
	    if user.usertype=='admin':
	    	return render(request,'admin-payment_all.html',{'orders':orders})
	    else:
	    	return render(request,'member-payment_all.html',{'orders':orders})
	    

def confirm_payment(order):
	if request.method == 'POST':
		order_id = request.POST.get('order_id')
		try:
			response = requests.get(f'https://api.razorpay.com/v1/orders/{order_id}', auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))
			response.raise_for_status()
			data = response.json()
			if 'status' not in data:
				logger.error(f"Invalid response data from Razorpay API: {data}")
				return False, 'Invalid response data from payment gateway.'
				if data['status'] == 'completed':
					logger.info(f"Payment confirmed for order ID {order_id}")
					return True, None
			else:
				logger.error(f"Payment status for order ID {order_id}: {data}")
				return False, data.get('error_description', 'Payment not confirmed.')
		except requests.exceptions.RequestException as e:
			logger.error(f"Payment gateway error: {str(e)}")
			return False, 'Error communicating with payment gateway. Please try again.'




def payment_success(request):
    msg = None  # Initialize msg to ensure it's always defined
    due_amount = None  # Initialize due_amount to ensure it's always defined
    order_id = None  # Initialize order_id to ensure it's always defined
    amount_float = None  # Initialize amount_float to ensure it's always defined

    if request.method == 'GET':
        email = request.session.get('email')
        if not email:
            return redirect('login')  # Redirect if email is not found

        try:
            user = User.objects.get(email=email)
            due_amount = user.due_amount  # Current due amount
            logger.debug("Current due amount: %s", due_amount)  # Log current due amount

            # Get amount and order_id from POST data
            amount_float = request.POST.get('amount')
            order_id = request.POST.get('order_id')
            logger.debug("Received amount: %s", amount_float)  # Log for debugging
            logger.debug("Received order_id: %s", order_id)  # Log received order_id

            if amount_float:
                try:
                    amount_float = float(amount)
                    logger.debug("Amount as float: %s", amount_float)  # Log converted amount
                    user.due_amount = due_amount - amount_float
                    logger.debug("New due amount before save: %s", user.due_amount)  # Log new due amount
                    user.save()  # Save updated user
                    request.session['due_amount'] = user.due_amount  # Update session variable
                    logger.debug("Updated due amount in session: %s", request.session['due_amount'])
                    msg = 'Payment Successful'

                    # Print order_id and amount to the command line
                    print(f"Order ID: {order_id}, Amount Paid: {amount_float}")
                    if user.usertype=='admin':
                    	return render(request, 'admin-payment_success.html', {
                        'msg': msg,
                        'due_amount': due_amount,
                        'order_id': order_id,
                        'amount_float': amount_float
                    })
                    else:
                    	return render(request, 'member-payment_success.html', {
                        	'msg': msg,
                        	'due_amount': due_amount,
                        	'order_id': order_id,
                        	'amount_float': amount_float
                    		})
                except ValueError:
                    msg = 'Invalid amount provided'
                    logger.error("Invalid amount provided: %s", amount)
            else:
                msg = 'Amount not provided'
                logger.error("Amount not provided in POST data.")

        except User.DoesNotExist:
            logger.error("User does not exist: %s", email)
            return redirect('login')  # Redirect if user does not exist

    # Handling for GET request or if POST fails
    return render(request, 'payment_success.html', {
        'msg': msg,
        'due_amount': due_amount,
        'order_id': order_id,
        'amount_float': amount_float
    })





def payment_failed(request):
    logger.error("Payment failed.")
    return render(request, 'payment_failed.html')




def gallery(request):
	user=User.objects.get(email=request.session['email'])
	images=Image.objects.all()
	if user.usertype=='admin':
		return render(request,'admin-gallery.html',{'images':images})
	else:
		return render(request,'gallery.html',{'images':images})

def create_gallery(request):
	if request.method=='POST' and request.FILES:
		for file in request.FILES.getlist('images'):
			Image.objects.create(image=file)
		return redirect ('gallery')
	else:
		return render(request,'create_gallery.html')