from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Le bot est en ligne !"

def run():
    app.run(host='0.0.0.0', port=10000)

# Lance le serveur web en tâche de fond
Thread(target=run).start()
import re
import asyncio
from highrise import BaseBot, User, Position, AnchorPosition
from highrise.models import SessionMetadata

class SuperBotHighrise(BaseBot):

    DESTINATIONS = {
        "entree": Position(x=3.5, y=0.0, z=3.5, facing="FrontRight"),
        "vip": Position(x=10.0, y=7.0, z=2.0, facing="FrontLeft"),
        "scene": Position(x=15.0, y=1.0, z=15.0, facing="FrontRight"),
        "bar": Position(x=2.0, y=0.0, z=12.0, facing="FrontRight"),
        "porte": Position(x=10.0, y=0.0, z=2.0, facing="FrontLeft")
    }

    EMOTES_CONFIG = {
        "wave": {"id": "emote-wave", "duration": 4.5},
        "hello": {"id": "emote-wave", "duration": 4.5},
        "dance": {"id": "dance-sexy", "duration": 6.0},
        "sing": {"id": "idle_singing", "duration": 8.5},
        "laugh": {"id": "emote-laughing", "duration": 4.0},
        "pose": {"id": "emote-pose7", "duration": 5.0},
        "clap": {"id": "emote-clap", "duration": 4.0},
        "hot": {"id": "emote-hot", "duration": 4.5},
        "think": {"id": "emote-thinking", "duration": 4.5},
        "rest": {"id": "sit-idle-cute", "duration": 6.0},
        "idlespace": {"id": "idle-space-float", "duration": 9.5},
        "energy": {"id": "dance-energy", "duration": 8.0},
        "kpop": {"id": "dance-blackpink", "duration": 7.5},
        "punk": {"id": "dance-punk", "duration": 6.5},
        "savage": {"id": "dance-tiktok", "duration": 7.0},
        "flex": {"id": "emote-flex", "duration": 4.0},
        "fight": {"id": "idle-martial-artist", "duration": 6.0},
        "sad": {"id": "emote-sad", "duration": 5.0},
        "relaxed": {"id": "inf-emote-relaxed", "duration": 6.0},
        "teleport": {"id": "emote-teleporting", "duration": 5.5},
        "twerkitout": {"id": "dance-twerk", "duration": 6.0},
        "kickingback": {"id": "sit-idle-laidBack", "duration": 7.5}
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.active_emotes = {}
        self.muted_users = set()
        self.bot_username = ""

    async def on_start(self, session_metadata: SessionMetadata) -> None:
        print("🤖 Bot connecté avec succès au salon Highrise !")

    async def on_user_join(self, user: User, position: Position | AnchorPosition) -> None:
        await self.highrise.chat(f"👋 Bonjour et bienvenue chez maître shadow , @{user.username} ! Passe un bon moment ! 🎉")

    async def on_user_leave(self, user: User) -> None:
        if user.id in self.active_emotes:
            self.active_emotes[user.id] = False
        if user.id in self.muted_users:
            self.muted_users.remove(user.id)

    async def run_emote_loop(self, user_id: str, emote_key: str):
        self.active_emotes[user_id] = True
        emote_id = self.EMOTES_CONFIG[emote_key]["id"]
        duration = self.EMOTES_CONFIG[emote_key]["duration"]
        while self.active_emotes.get(user_id, False):
            try:
                await self.highrise.send_emote(emote_id, user_id)
            except Exception:
                break
            await asyncio.sleep(duration)

    async def get_user_status(self, user_id: str) -> tuple[bool, bool]:
        try:
            permissions = await self.highrise.get_room_privileges(user_id)
            return permissions.content.moderator, permissions.content.owner
        except Exception:
            return False, False
    async def on_chat(self, user: User, message: str) -> None:
        # Récupération automatique et sécurisée du nom du bot s'il n'est pas encore défini
        if not self.bot_username:
            try:
                room_users = await self.highrise.get_room_users()
                for u, pos in room_users.content:
                    # Le bot se repère lui-même dans la liste grâce à son ID unique
                    if u.id == self.id:
                        self.bot_username = u.username.lower()
                        break
            except Exception:
                pass

        if user.id in self.muted_users:
            return

        msg_clean = message.strip()
        parts = msg_clean.split()
        if not parts:
            return

        command = parts[0].lower()

        if command in ["!tp", "!teleport"]:
            target_is_bot = False
            target_user = None
            lieu = "entree"

            if len(parts) > 1 and parts[1].startswith("@"):
                target_username = parts[1].replace("@", "").strip().lower()
                if self.bot_username and target_username == self.bot_username:
                    target_is_bot = True
                else:
                    room_users = await self.highrise.get_room_users()
                    for u, pos in room_users.content:
                        if u.username.lower() == target_username:
                            target_user = u
                            break
                    if not target_user and not target_is_bot:
                        await self.highrise.chat(f"❌ Impossible de trouver @{parts[1].replace('@', '')} ici.")
                        return
                if len(parts) > 2:
                    lieu = parts[2].lower()
            elif len(parts) > 1:
                lieu = parts[1].lower()
                target_user = user

            if target_user is None and not target_is_bot:
                target_user = user

            if lieu in self.DESTINATIONS:
                is_mod, is_owner = await self.get_user_status(user.id)

                if target_is_bot:
                    if not (is_mod or is_owner):
                        await self.highrise.chat(f"❌ Désolé @{user.username}, seul le staff peut déplacer le bot !")
                        return
                    if lieu == "bar":
                        await self.highrise.chat("🤖 Je ne peux pas m'envoyer moi-même au bar !")
                        return
                    await self.highrise.chat(f"🚶‍♂️ Bien reçu, je me déplace pas à pas vers : {lieu} !")
                    await self.highrise.walk_to(self.DESTINATIONS[lieu])
                    return

                if lieu == "bar":
                    if not (is_mod or is_owner):
                        await self.highrise.chat(f"❌ Désolé @{user.username}, seul le staff peut envoyer quelqu'un au bar !")
                        return
                    self.muted_users.add(target_user.id)
                    self.active_emotes[target_user.id] = False 
                    await self.highrise.teleport(target_user.id, self.DESTINATIONS[lieu])
                    await self.highrise.chat(f"🚷 @{target_user.username} a été envoyé au bar et réduit au silence !")
                else:
                    if target_user.id in self.muted_users:
                        self.muted_users.remove(target_user.id)
                    await self.highrise.teleport(target_user.id, self.DESTINATIONS[lieu])
                    await self.highrise.chat(f"✨ @{target_user.username} a été téléporté à : {lieu} !")
            else:
                await self.highrise.chat(f"❌ Destination inconnue. Lieux disponibles : {', '.join([k for k in self.DESTINATIONS.keys() if k != 'bar'])}")

        elif command in self.EMOTES_CONFIG:
            self.active_emotes[user.id] = False
            await asyncio.sleep(0.2)
            asyncio.create_task(self.run_emote_loop(user.id, command))
            await self.highrise.chat(f"🕺 Émote '{command}' activée en continu pour @{user.username} ! (!stop pour arrêter)")

        elif command == "!stop":
            if user.id in self.active_emotes and self.active_emotes[user.id]:
                self.active_emotes[user.id] = False
                await self.highrise.chat(f"🛑 Émote arrêtée pour @{user.username}.")
            else:
                await self.highrise.chat(f"❓ Tu n'as pas d'émote active en boucle, @{user.username}.")

        elif command in ["!copy", "!copier"]:
            if len(parts) < 2:
                await self.highrise.chat("❌ Usage: !copy @pseudo")
                return
            target_username = parts[1].replace("@", "").strip()
            room_users = await self.highrise.get_room_users()
            found_user = None
            for u, pos in room_users.content:
                if u.username.lower() == target_username.lower():
                    found_user = u
                    break
            if not found_user:
                await self.highrise.chat(f"❌ Impossible de trouver @{target_username} dans le salon.")
                return

            try:
                target_outfit = await self.highrise.get_user_outfit(found_user.id)
                bot_outfit = await self.highrise.get_user_outfit(self.id)
                new_outfit = []
                unclonable_items = 0
                for item in target_outfit.outfit:
                    if hasattr(item, 'clonable') and not item.clonable:
                        unclonable_items += 1
                    else:
                        new_outfit.append(item)
                if unclonable_items > 0:
                    for bot_item in bot_outfit.outfit:
                        if bot_item.type not in [i.type for i in new_outfit]:
                            new_outfit.append(bot_item)
                await self.highrise.set_outfit(new_outfit)
                if unclonable_items > 0:
                    await self.highrise.chat(f"🧥 J'ai copié le style de @{found_user.username}, mais {unclonable_items} article(s) n'ont pas pu être copiés.")
                else:
                    await self.highrise.chat(f"🔥 Style de @{found_user.username} entièrement copié avec succès !")
            except Exception as e:
                await self.highrise.chat("❌ Une erreur est survenue en tentant de copier cette tenue.")
