from rest_framework.exceptions import NotFound

def get_player_actor(user):
    try:
        return user.actor
    except AttributeError:
        raise NotFound("У вас ещё нет персонажа")