
# idk if we want to use controllers:
class UserController:

    async def create_user(self, request):
        data = await request.json()
        user = "rocking like a hurricane"
        return user 