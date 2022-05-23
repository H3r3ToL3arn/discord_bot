import discord
from rich import print
import pandas as pd
import datetime
import notify2
import argparse
import requests
import shutil
import os
from os import listdir
from notify2 import EXPIRES_NEVER

ROOT_DIR = os.path.dirname(__file__)

# Help text for --help command
help_text = "This is a discord bot that is intended to retrieve the messages that the user receives and display only those whose channel is indicated in a VIP list."

# Initiate the parser
parser = argparse.ArgumentParser(description=help_text)
parser.add_argument("-L", "--listen", help="Listen to discord and display messages from the VIP list", action="store_true")
parser.add_argument("-G", "--get_channels", help="Fetching user channels", action="store_true")
parser.add_argument("-I", "--icon_update", help="Update servers icon", action="store_true")

# Read arguments from the command line
args = parser.parse_args()

token = os.environ.get('DISCORD_TOKEN')
client = discord.Client()
now = datetime.datetime.now()
notify2.init('💬 Discord Bot - Nouveau message !')

# Définition du chemin de sauvegarde des icons
path = f"{ROOT_DIR}/icon/"

@client.event
async def on_ready():
    print('✅ We have logged in as {0.user}'.format(client))
    # If user want to update the channel list    
    if args.get_channels:
        # Création d'une liste de dictionnaire contenant les informations pertinentes
        list_dict_csv = []
        for guild in client.guilds:
            for channel in guild.channels:
                if isinstance(channel, discord.channel.TextChannel) and channel.name.startswith('ticket') == False:
                    list_dict_csv.append({
                        'server_id' : guild.id,
                        'server_name (guild.name)': guild.name,
                        'channel_id': channel.id,
                        'channel_name': channel.name,
                    })

        # Extraction des informations dans un fichier csv via un DataFrame Panda
        output = pd.DataFrame(list_dict_csv)
        output.to_csv(f'{ROOT_DIR}/output.csv')
        print("✅ Channels list succesfully updated !")
        # Stopping the program
        await client.close()

    # If user want to update the servers icon database
    elif args.icon_update:
        # Création d'un DataFrame Panda via un fichier CSV mis à jour à la mano
        VIP_list = pd.read_csv(f'{ROOT_DIR}/VIP_list.csv')
        # Récupération de la liste des icon déjà téléchargés
        icon_list = [f for f in listdir(path)]
        # Définition d'un header personnalisé pour se voir autorisé le téléchargement par le site web
        headers = {
            'User-Agent' : 'Mozilla/5.0 (iPhone; CPU iPhone OS 7_0 like Mac OS X; en-us) AppleWebKit/537.51.1 (KHTML, like Gecko) Version/7.0 Mobile/11A465 Safari/9537.53'
        }

        # Pour chaque serveur de l'utilisateur
        for guild in client.guilds:
            # Vérifier s'il est dans la liste VIP
            if VIP_list.isin({'server_id': [guild.id]}).any().any():
                print(f"💾 Downloading \"{guild.name}\" icon...")
                # Vérifier si son icone est déjà téléchargé
                if str(guild.id) in icon_list:
                    print("☑ Already downloaded !")
                # Sinon télécharger l'icone
                else:
                    r = requests.get(f"{guild.icon_url}", headers=headers, stream=True)
                    if r.status_code == 200:
                        with open(f"{path}{guild.id}", 'wb') as f:
                            r.raw.decode_content = True
                            shutil.copyfileobj(r.raw, f)
                            print('✅ Success !')
                    else:
                        print('🚫 An error has occured')
        # Fermer le client à la fin du téléchargement
        await client.close()
                
                
    # If user want to display messages from the VIP_list
    elif args.listen:
        print("💬 Fetching messages...")
        @client.event
        async def on_message(message):
        # Importation du fichier trié qui servira de filtre
            VIP_list = pd.read_csv(f'{ROOT_DIR}/VIP_list.csv')
            # Si le message est de moi-même, ne rien faire
            if message.author == client.user:
                return
            # Si le message provient d'un channel présent dans la liste triée VIP_list.csv, alors l'afficher dans la console et envoyer une notification desktop
            elif VIP_list.isin({'channel_id': [message.channel.id]}).any().any() and VIP_list.isin({'server_id': [message.guild.id]}).any().any():
                print(now.strftime("%Y-%m-%d %H:%M:%S"), f"| {message.guild.name} | {message.channel.name} | {message.author.name}\nhttps://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}")
                notif = notify2.Notification(f"{message.guild.name} | {message.channel.name} | {message.author.name}", f"<a href=\"https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}\">lien </a>", icon=f"{path}{message.guild.id}")
                notif.set_timeout(EXPIRES_NEVER)
                notif.show()
client.run(token, bot=False)









