from agentmake import agentmake

riddle = "If you look you cannot see me. And if you see me you cannot see anything else. I can make anything you want happen, but later everything goes back to normal. What am I?"

print(f"Riddle: {riddle}\n\nAnswer:")

agentmake(riddle, system="reasoning")