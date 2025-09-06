from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Message
import json
from django.contrib.auth.models import User
from . import agent
import pandas
agent = agent.Agent()


def home(request):
    datasets = ['230516.xlsx', '230517.xlsx', '230518.xlsx', '230519.xlsx', '230520.xlsx', '230521.xlsx']
    return render(request,'home.html', {'user':request.user, 'datasets':datasets})


# Chat room view: renders the UI and shows last 50 messages
def chat_room(request, room_name):
    messages = Message.objects.filter(room_name=room_name).order_by('timestamp')[:50]
    return render(request, "chat.html", {
        "room_name": room_name,
        "messages": messages
    })

# Save new message via POST
@csrf_exempt
def send_message(request):
    if request.method == "POST":
        data = json.loads(request.body)
        room = data.get("room_name")
        content = data.get("message")
        user = request.user if request.user.is_authenticated else None

        msg = Message.objects.create(room_name=room, user=user, content=content)
        print('Human message:', msg)
        bot_reply = agent.implementor(message = msg)
        bot_msg = Message.objects.create(room_name=room, user=None, content=bot_reply['content'])
        print(bot_msg)
        return JsonResponse({
            "user_message": {
                "id": msg.id,
                "user": user.username if user else "Anonymous",
                "content": content,
                "timestamp": msg.timestamp.strftime("%H:%M:%S"),
            },
            "bot_message": {
                "id": bot_msg.id,
                "user": "Assistant",
                "content": bot_reply['content'],
                "timestamp": bot_msg.timestamp.strftime("%H:%M:%S"),
                "type": bot_reply['type']
            }
        })
    return JsonResponse({"error": "Invalid request"}, status=400)


# Optional: fetch new messages via GET (for simple "real-time" polling)
def get_messages(request, room_name):
    last_id = request.GET.get("last_id", 0)
    messages = Message.objects.filter(room_name=room_name, id__gt=last_id).order_by('timestamp')
    data = [{
        "id": m.id,
        "user": m.user.username if m.user else "Anonymous",
        "content": m.content,
        "timestamp": m.timestamp.strftime("%H:%M:%S")
    } for m in messages]
    return JsonResponse(data, safe=False)