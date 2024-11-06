from django.shortcuts import render,redirect
import requests

# Create your views here.


def admin_index(request):
    # Example context data
    context = {
        'discussion': {'id': 6},  # Replace with actual discussion data
        'comments': [
            {'id': 32},
            {'id': 33},
        ],
    }

    return render(request, 'admin-index.html',context,{'discussion':discussion})


def index(request,discussion_id):
	context = {
        'discussion': {'id': 6},  # Replace with actual discussion data
        'comments': [
            {'id': 32},
            {'id': 33},
        ],
    }

	return render(request,'index.html',context)

def disc_insert(request):
	url='http://localhost:8001/myapp/discussion'
	if request.method=='POST':
		
		querystring={'title':request.POST.get('title'),'content':request.POST.get('content'),'created_at':request.POST.get('created_at'),'author':request.POST.get('author'),}
		response=requests.post(url,json=querystring)
		print(response)

		msg='Discussion Inserted Successfully' if response.status_code== 201 else 'Failed to create discussion'

		return render(request,'disc-insert.html',{'msg':msg})
		 
	else:
		response = requests.get(url)
		discussions = response.json()
		return render(request,'disc-insert.html',{'discussions':discussions})
		

BASE_URL = 'http://localhost:8001/myapp'

def comm_insert(request, discussion_id):
    # Fetch discussion data
    discussion_response = requests.get(f'{BASE_URL}/discussion/{discussion_id}')
    discussion = discussion_response.json() if discussion_response.status_code == 200 else None


    # Fetch comments
    comment_response = requests.get(f"{BASE_URL}/comment?discussion={discussion_id}")
    comments = comment_response.json() if comment_response.status_code == 200 else []
    


    if request.method == 'POST':
        content = request.POST.get('content')
        created_at = request.POST.get('created_at')
        author = request.POST.get('author')

        # Basic input validation
        if content and created_at and author:
            querystring = {
                'discussion': discussion_id,
                'content': content,
                'created_at': created_at,
                'author': author,
            }
            response = requests.post(f"{BASE_URL}/comment", json=querystring)

            if response.status_code == 201:  # Assuming 201 Created for success
                msg = 'Comment Inserted Successfully'
                return redirect('comm-insert', discussion_id=discussion_id)  # Redirect to avoid resubmission
            else:
                msg = 'Failed to insert comment.'

        else:
            msg = 'All fields are required.'

        return render(request, 'comm-insert.html', {
            'msg': msg,
            'discussion': discussion,
            'discussion_id': discussion_id,
            'comments': comments,
        })

    return render(request, 'comm-insert.html', {
        'discussion': discussion,
        'discussion_id': discussion_id,
        'comments': comments,
    })
BASE_URL = 'http://localhost:8001/myapp'
def rem_comm(request,discussion_id,comment_id):
	if request.method == 'POST':
		delete_url = f"{BASE_URL}/comment/{comment_id}"
		response = requests.delete(delete_url)
		if response.status_code == 204:
			msg = 'Comment deleted successfully.'
		else:
			msg = 'Failed to delete comment.'
		return redirect('comm-insert', discussion_id=discussion_id)
	discussion_response = requests.get(f"{BASE_URL}/discussion/{discussion_id}")
	discussion = discussion_response.json() if discussion_response.status_code == 200 else None
	comment_response = requests.get(f"{BASE_URL}/comment?discussion={discussion_id}")
	comments = [comment for comment in comment_response.json()] if comment_response.status_code == 200 else []
	return render(request, 'rem-comm.html', {
        'discussion': discussion,
        'discussion_id': discussion_id,
        'comments': comments,
        'comment_id': comment_id
    })