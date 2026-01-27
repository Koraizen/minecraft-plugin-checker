import requests
import json
import time
import os
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Dict, List, Optional
import re
import random

class PluginUpdateChecker:
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        self.data_file = "plugin_versions.json"
        self.seen_updates = self.load_seen_updates()
        self.check_counter = 0
        self.is_first_run = not os.path.exists(self.data_file)
        
        # SİZİN TAKİP EDİLECEK PLUGİNLERİNİZ (GÜNCEL VE DETAYLI)
        self.tracked_plugins = {
            # ===== SPIGOT PLUGINS =====
            "MinePacksBackpack": {"spigot_id": "19286"},
            "AdvancedPortals": {"spigot_id": "14356"},
            "AlwaysNightVision": {"spigot_id": "117478"},
            "AntiPluginLookup": {"spigot_id": "63007"},
            "AutoPickup": {"spigot_id": "7623"},
            "AxAFKZone": {"spigot_id": "119868"},
            "AxAuctions": {"spigot_id": "115308"},
            "AxInventoryRestore": {"spigot_id": "111975"},
            "AxKills": {"spigot_id": "112119"},
            "AxTrade": {"spigot_id": "116826"},
            "BanItem": {"spigot_id": "67701"},
            "BlueSlimeCore": {"spigot_id": "83189"},
            "LiteChatGames": {"spigot_id": "105831"},
            "ChatSentry": {"spigot_id": "79616"},
            "Citizens": {"spigot_id": "13811", "github_repo": "CitizensDev/Citizens2"},
            "ClearLag": {"spigot_id": "68271"},
            "CobwebRemoveBoxPVP": {"spigot_id": "120452"},
            "CombatLogX": {"spigot_id": "31689", "modrinth_slug": "combatlogx"},
            "DamageIndicator": {"spigot_id": "87113"},
            "DecentHolograms": {"spigot_id": "96927", "modrinth_slug": "decentholograms"},
            "DeluxeMenus": {"spigot_id": "11734", "modrinth_slug": "deluxemenus"},
            "Duels": {"spigot_id": "20171", "modrinth_slug": "duels"},
            "ExcellentCrates": {"spigot_id": "48732", "modrinth_slug": "excellentcrates"},
            "FastAsyncWorldEdit": {"spigot_id": "13932", "modrinth_slug": "fastasyncworldedit"},
            "DupeFixes": {"spigot_id": "44411", "modrinth_slug": "illegalstack"},
            "InfiniteAnnouncements": {"spigot_id": "71266", "modrinth_slug": "infiniteannouncements"},
            "InteractiveChat": {"spigot_id": "75870", "modrinth_slug": "interactivechat"},
            "InvSee": {"spigot_id": "82342", "modrinth_slug": "invseplusplus"},
            "ItemEdit": {"spigot_id": "40993"},
            "ItemTag": {"spigot_id": "89634"},
            "LiteBans": {"spigot_id": "3715", "modrinth_slug": "litebans"},
            "LPCChatFormatter": {"spigot_id": "68965", "modrinth_slug": "lpc"},
            "LuckPerms": {"spigot_id": "28140", "modrinth_slug": "luckperms", "github_repo": "LuckPerms/LuckPerms"},
            "Multiverse-Core": {"spigot_id": "390", "modrinth_slug": "multiverse-core"},
            "MyCommand": {"spigot_id": "22272", "modrinth_slug": "mycommand"},
            "PlaceholderAPI": {"spigot_id": "6245", "modrinth_slug": "placeholderapi", "github_repo": "PlaceholderAPI/PlaceholderAPI"},
            "PlayerVaults": {"spigot_id": "9228", "modrinth_slug": "playervault"},
            "PlugManX": {"spigot_id": "88135"},
            "ProtocolLib": {"spigot_id": "1997", "modrinth_slug": "protocollib", "github_repo": "dmulloy2/ProtocolLib"},
            "RealMines": {"spigot_id": "73707", "modrinth_slug": "realmines"},
            "Shopkeepers": {"spigot_id": "80756"},
            "TAB": {"spigot_id": "57806", "modrinth_slug": "tab"},
            "TaskScheduler": {"spigot_id": "115092"},
            "ThemisAntiCheat": {"spigot_id": "90766"},
            "ViaBackwards": {"spigot_id": "27448", "modrinth_slug": "viabackwards", "github_repo": "ViaVersion/ViaBackwards"},
            "ViaVersion": {"spigot_id": "19254", "modrinth_slug": "viaversion", "github_repo": "ViaVersion/ViaVersion"},
            "NuVotifier": {"spigot_id": "13449", "modrinth_slug": "votifier"},
            "VotingPlugin": {"spigot_id": "15358", "modrinth_slug": "votingplugin"},
            "RankUp": {"spigot_id": "17933", "modrinth_slug": "rankup"},
            "SilkSpawners": {"spigot_id": "60063"},
            "Vulcan": {"spigot_id": "83626", "modrinth_slug": "vulcan"},
            "CoreProtect": {"spigot_id": "8631", "modrinth_slug": "coreprotect"},
            "Dynmap": {"spigot_id": "274", "modrinth_slug": "dynmap"},
            "MythicMobs": {"spigot_id": "5702", "modrinth_slug": "mythicmobs"},
            "RoseStacker": {"spigot_id": "82729", "modrinth_slug": "rosestacker"},
            "EconomyShopGUI": {"spigot_id": "69927", "modrinth_slug": "economyshopgui"},
            "AdvancedEnchantments": {"spigot_id": "43058", "modrinth_slug": "advancedenchantments"},
            "UltimateAutoRestart": {"spigot_id": "74051", "modrinth_slug": "ultimateautorestart"},
            "SimplePortals": {"spigot_id": "56772", "modrinth_slug": "simpleportals"},
            "DiscordSRV": {"spigot_id": "18494", "modrinth_slug": "discord", "github_repo": "DiscordSRV/DiscordSRV"},
            
            # ===== EK MODRINTH PLUGINS =====
            "EssentialsX": {"modrinth_slug": "essentialsx", "github_repo": "EssentialsX/Essentials"},
            "Vault": {"modrinth_slug": "vault", "github_repo": "MilkBowl/Vault"},
            "WorldEdit": {"modrinth_slug": "worldedit", "github_repo": "EngineHub/WorldEdit"},
            "WorldGuard": {"modrinth_slug": "worldguard", "github_repo": "EngineHub/WorldGuard"},
            "GSit": {"modrinth_slug": "gsit"},
            "ItemsAdder": {"modrinth_slug": "itemsadder"},
            "Nightcore": {"modrinth_slug": "nightcore"},
            "DailyRewards": {"modrinth_slug": "dailyrewards"},
            "EssentialsSpawn": {"modrinth_slug": "essentialsspawn"},
            "EventBridge": {"modrinth_slug": "eventbridge"},
            "Farmer": {"modrinth_slug": "farmer"},
            "FreedomChat": {"modrinth_slug": "freedomchat"},
            "Images": {"modrinth_slug": "images"},
            "ItemsHider": {"modrinth_slug": "itemshider"},
            "LeaderOS": {"modrinth_slug": "leaderos"},
            "LitLibs": {"modrinth_slug": "litlibs"},
            "LitMinions": {"modrinth_slug": "litminions"},
            "Menus": {"modrinth_slug": "menus"},
            "NBTMfi": {"modrinth_slug": "nbtmfi"},
            "OBTaskManager": {"modrinth_slug": "obtaskmanager"},
            "DailyQuests": {"modrinth_slug": "dailyquests"},
            "OFProtection": {"modrinth_slug": "ofprotection"},
            "PacketEvents": {"modrinth_slug": "packetevents"},
            "PremiumAds": {"modrinth_slug": "premiumads"},
            "QuickShopHikari": {"modrinth_slug": "quickshop-hikari"},
            "SimpleVoiceChat": {"modrinth_slug": "voicechat"},
            "XPBottle": {"modrinth_slug": "xpbottle"},
            "Geyser": {"modrinth_slug": "geyser", "github_repo": "GeyserMC/Geyser"},
            "Floodgate": {"modrinth_slug": "floodgate", "github_repo": "GeyserMC/Floodgate"},
            "Chunky": {"modrinth_slug": "chunky"},
            "GrimAC": {"modrinth_slug": "grimac"},
            "KnockbackSync": {"modrinth_slug": "knockbacksync"},
            "AdvancedTeleport": {"modrinth_slug": "advancedteleport"},
            "AntiAFK": {"modrinth_slug": "antiafk"},
            "Abanseme": {"modrinth_slug": "abanseme"},
            "AdvancedChests": {"modrinth_slug": "advancedchests"},
            "AdvancedOrder": {"modrinth_slug": "advancedorder"},
            "AdvancementAnnouncer": {"modrinth_slug": "advancementannouncer"},
            "ARBlockerBlocker": {"modrinth_slug": "arblockerblocker"},
            "AllMesaj": {"modrinth_slug": "allmesaj"},
            "AJParkour": {"modrinth_slug": "ajparkour"},
            "AntiHeadstoneClock": {"modrinth_slug": "antiheadstoneclock"},
            "AntiSunger": {"modrinth_slug": "antisunger"},
            "ADFLimiter": {"modrinth_slug": "adflimiter"},
            "BankMenu": {"modrinth_slug": "bankmenu"},
            "SaesonalRankup": {"modrinth_slug": "saesonalrankup"},
            "Alestesi": {"modrinth_slug": "alestesi"},
            "AltasCoin": {"modrinth_slug": "altascoin"},
            "AtlasLauncher": {"modrinth_slug": "atlaslauncher"},
            "AtlasModeration": {"modrinth_slug": "atlasmoderation"},
            "EVoterParty": {"modrinth_slug": "evoterparty"},
            "AxFunctions": {"modrinth_slug": "axfunctions"},
            "AxNewards": {"modrinth_slug": "axnewards"},
            "BattlePasses": {"modrinth_slug": "battlepasses"},
            "BentoBox": {"modrinth_slug": "bentobox"},
            "BentoBoxBank": {"modrinth_slug": "bentobox-bank"},
            "BentoBoxBorder": {"modrinth_slug": "bentobox-border"},
            "BentoBoxBSkyBlock": {"modrinth_slug": "bentobox-bskyblock"},
            "BentoBoxChat": {"modrinth_slug": "bentobox-chat"},
            "BentoBoxLevel": {"modrinth_slug": "bentobox-level"},
            "BentoBoxLimits": {"modrinth_slug": "bentobox-limits"},
            "BentoBoxBiomes": {"modrinth_slug": "bentobox-biomes"},
            "ChatGentry": {"modrinth_slug": "chatgentry"},
            "CommandManager": {"modrinth_slug": "commandmanager"},
            "CrazyCrvous": {"modrinth_slug": "crazycrvous"},
            "DonutOrder": {"modrinth_slug": "donutoorder"},
            "Elevator": {"modrinth_slug": "elevator"},
            
            # ===== POLYMART PLUGINS =====
            "UltimateClans": {"polymart_id": "1162"},
            
            # ===== GITHUB REPOS =====
            "SiegeWar": {"github_repo": "TownyAdvanced/SiegeWar"}
        }

    def load_seen_updates(self) -> Dict:
        """Daha önce görülen güncellemeleri yükle"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def save_seen_updates(self):
        """Görülen güncellemeleri kaydet"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.seen_updates, f, indent=2, ensure_ascii=False)

    def get_platform_emoji(self, platform: str) -> str:
        """Platform için emoji döndür"""
        emojis = {
            "SpigotMC": "🟠",
            "Modrinth": "🟢",
            "Polymart": "🟣",
            "GitHub": "⚫"
        }
        return emojis.get(platform, "📦")

    def get_platform_color(self, platform: str) -> int:
        """Platform için renk kodu döndür"""
        colors = {
            "SpigotMC": 0xFF9500,  # Turuncu
            "Modrinth": 0x1BD96A,  # Yeşil
            "Polymart": 0xEB459E,  # Pembe
            "GitHub": 0x238636    # Koyu yeşil
        }
        return colors.get(platform, 0x5865F2)

    def check_spigot_updates(self) -> List[Dict]:
        """SpigotMC'deki pluginleri kontrol et"""
        updates = []
        
        try:
            spigot_plugins = [p for p in self.tracked_plugins.items() if 'spigot_id' in p[1]]
            print(f"   📡 SpigotMC kontrol ediliyor... ({len(spigot_plugins)} plugin)")
            
            for plugin_name, info in spigot_plugins:
                resource_id = info['spigot_id']
                
                try:
                    url = f"https://api.spiget.org/v2/resources/{resource_id}/versions/latest"
                    response = requests.get(url, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        version = data.get('name', 'Unknown')
                        
                        update_key = f"spigot_{resource_id}_{version}"
                        
                        if update_key not in self.seen_updates:
                            self.seen_updates[update_key] = datetime.now(timezone.utc).isoformat()
                            
                            updates.append({
                                "name": plugin_name,
                                "platform": "SpigotMC",
                                "version": version,
                                "url": f"https://www.spigotmc.org/resources/{resource_id}/",
                                "resource_id": resource_id,
                            })
                            
                            if self.is_first_run:
                                print(f"   ➜ Bulundu: {plugin_name} v{version}")
                            else:
                                print(f"   ✓ Yeni güncelleme: {plugin_name} v{version}")
                    
                    time.sleep(0.3)
                    
                except Exception as e:
                    print(f"   ⚠ {plugin_name} hatası: {str(e)[:50]}")
            
            print(f"   → {len(updates)} plugin bulundu")
                
        except Exception as e:
            print(f"   ✗ SpigotMC hatası: {e}")
        
        return updates

    def check_modrinth_updates(self) -> List[Dict]:
        """Modrinth'deki pluginleri kontrol et"""
        updates = []
        
        try:
            modrinth_plugins = [p for p in self.tracked_plugins.items() if 'modrinth_slug' in p[1]]
            print(f"   📡 Modrinth kontrol ediliyor... ({len(modrinth_plugins)} plugin)")
            
            for plugin_name, info in modrinth_plugins:
                slug = info['modrinth_slug']
                
                try:
                    url = f"https://api.modrinth.com/v2/project/{slug}/version"
                    response = requests.get(url, timeout=10)
                    
                    if response.status_code == 200:
                        versions = response.json()
                        if versions:
                            latest = versions[0]
                            version = latest.get('version_number', 'Unknown')
                            
                            update_key = f"modrinth_{slug}_{version}"
                            
                            if update_key not in self.seen_updates:
                                self.seen_updates[update_key] = datetime.now(timezone.utc).isoformat()
                                
                                updates.append({
                                    "name": plugin_name,
                                    "platform": "Modrinth",
                                    "version": version,
                                    "url": f"https://modrinth.com/plugin/{slug}",
                                    "changelog": latest.get('changelog', ''),
                                    "downloads": latest.get('downloads', 0),
                                })
                                
                                if self.is_first_run:
                                    print(f"   ➜ Bulundu: {plugin_name} v{version}")
                                else:
                                    print(f"   ✓ Yeni güncelleme: {plugin_name} v{version}")
                    
                    time.sleep(0.3)
                    
                except Exception as e:
                    print(f"   ⚠ {plugin_name} hatası: {str(e)[:50]}")
            
            print(f"   → {len(updates)} plugin bulundu")
                
        except Exception as e:
            print(f"   ✗ Modrinth hatası: {e}")
        
        return updates

    def check_polymart_updates(self) -> List[Dict]:
        """Polymart'daki pluginleri kontrol et"""
        updates = []
        
        try:
            polymart_plugins = [p for p in self.tracked_plugins.items() if 'polymart_id' in p[1]]
            print(f"   📡 Polymart kontrol ediliyor... ({len(polymart_plugins)} plugin)")
            
            for plugin_name, info in polymart_plugins:
                resource_id = info['polymart_id']
                
                try:
                    url = f"https://api.polymart.org/v1/getResourceInfo/?resource_id={resource_id}"
                    headers = {"User-Agent": "Mozilla/5.0"}
                    response = requests.get(url, headers=headers, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        resource = data.get('response', {}).get('resource', {})
                        version = resource.get('version', 'Unknown')
                        
                        update_key = f"polymart_{resource_id}_{version}"
                        
                        if update_key not in self.seen_updates:
                            self.seen_updates[update_key] = datetime.now(timezone.utc).isoformat()
                            
                            updates.append({
                                "name": plugin_name,
                                "platform": "Polymart",
                                "version": version,
                                "url": f"https://polymart.org/resource/{resource_id}",
                            })
                            
                            if self.is_first_run:
                                print(f"   ➜ Bulundu: {plugin_name} v{version}")
                            else:
                                print(f"   ✓ Yeni güncelleme: {plugin_name} v{version}")
                    
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"   ⚠ {plugin_name} hatası: {str(e)[:50]}")
            
            print(f"   → {len(updates)} plugin bulundu")
                
        except Exception as e:
            print(f"   ✗ Polymart hatası: {e}")
        
        return updates

    def check_github_updates(self) -> List[Dict]:
        """GitHub'daki pluginleri kontrol et"""
        updates = []
        
        try:
            github_plugins = [p for p in self.tracked_plugins.items() if 'github_repo' in p[1]]
            print(f"   📡 GitHub kontrol ediliyor... ({len(github_plugins)} plugin)")
            
            for plugin_name, info in github_plugins:
                repo = info['github_repo']
                
                try:
                    url = f"https://api.github.com/repos/{repo}/releases/latest"
                    headers = {"Accept": "application/vnd.github.v3+json"}
                    response = requests.get(url, headers=headers, timeout=10)
                    
                    if response.status_code == 200:
                        release = response.json()
                        tag_name = release.get('tag_name', 'Unknown')
                        
                        update_key = f"github_{repo}_{tag_name}"
                        
                        if update_key not in self.seen_updates:
                            self.seen_updates[update_key] = datetime.now(timezone.utc).isoformat()
                            
                            updates.append({
                                "name": plugin_name,
                                "platform": "GitHub",
                                "version": tag_name,
                                "url": release.get('html_url', f"https://github.com/{repo}"),
                                "changelog": release.get('body', ''),
                                "author": release.get('author', {}).get('login', 'Unknown'),
                            })
                            
                            if self.is_first_run:
                                print(f"   ➜ Bulundu: {plugin_name} {tag_name}")
                            else:
                                print(f"   ✓ Yeni release: {plugin_name} {tag_name}")
                    
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"   ⚠ {plugin_name} hatası: {str(e)[:50]}")
            
            print(f"   → {len(updates)} plugin bulundu")
                
        except Exception as e:
            print(f"   ✗ GitHub hatası: {e}")
        
        return updates

    def send_discord_notification(self, update_info: Dict):
        """Discord'a güzel bir güncelleme bildirimi gönder"""
        
        platform = update_info['platform']
        emoji = self.get_platform_emoji(platform)
        color = self.get_platform_color(platform)
        
        # Başlık ve açıklama
        if self.is_first_run:
            title = f"{emoji} {update_info['name']}"
            description = f"**Mevcut Versiyon:** `{update_info['version']}`"
        else:
            title = f"🎉 {update_info['name']} Güncellendi!"
            description = f"**Yeni versiyon yayınlandı!**"
        
        # Field'ler
        fields = [
            {
                "name": "📌 Versiyon",
                "value": f"```{update_info['version']}```",
                "inline": True
            },
            {
                "name": f"{emoji} Platform",
                "value": f"**{platform}**",
                "inline": True
            }
        ]
        
        # Downloads bilgisi (Modrinth için)
        if update_info.get('downloads'):
            fields.append({
                "name": "📥 İndirmeler",
                "value": f"`{update_info['downloads']:,}`",
                "inline": True
            })
        
        # Resource ID (Spigot için)
        if update_info.get('resource_id'):
            fields.append({
                "name": "🆔 Resource ID",
                "value": f"`{update_info['resource_id']}`",
                "inline": True
            })
        
        # Author (GitHub için)
        if update_info.get('author'):
            fields.append({
                "name": "👤 Yazar",
                "value": f"`{update_info['author']}`",
                "inline": True
            })
        
        # Changelog
        if update_info.get('changelog') and update_info['changelog'].strip():
            changelog = update_info['changelog'][:300]
            if len(update_info['changelog']) > 300:
                changelog += "..."
            
            # Markdown formatını temizle
            changelog = changelog.replace('```', '`').replace('**', '')
            
            fields.append({
                "name": "📝 Değişiklik Notları",
                "value": f"```{changelog}```" if changelog else "_Bilgi yok_",
                "inline": False
            })
        
        # Download butonu
        fields.append({
            "name": "⬇️ İndirme Linki",
            "value": f"**[Buraya tıklayarak indir]({update_info['url']})**",
            "inline": False
        })
        
        embed = {
            "title": title,
            "description": description,
            "color": color,
            "fields": fields,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "footer": {
                "text": f"Plugin Update Checker • {platform}",
                "icon_url": "https://cdn.discordapp.com/emojis/1234567890.png"  # İsteğe bağlı
            },
            "thumbnail": {
                "url": "https://static.spigotmc.org/img/spigot-og.png" if platform == "SpigotMC" else None
            }
        }
        
        # Thumbnail'i temizle eğer None ise
        if not embed["thumbnail"]["url"]:
            del embed["thumbnail"]

        payload = {
            "username": "🤖 Plugin Update Bot",
            "avatar_url": "https://i.imgur.com/4M34hi2.png",  # İsteğe bağlı bot avatarı
            "embeds": [embed]
        }

        try:
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            if response.status_code == 204:
                print(f"      ✓ Discord'a gönderildi")
            else:
                print(f"      ✗ Discord hatası: {response.status_code}")
        except Exception as e:
            print(f"      ✗ Gönderim hatası: {str(e)[:50]}")

    def check_all_updates(self):
        """Tüm platformlardaki güncellemeleri kontrol et"""
        print(f"\n{'='*70}")
        print(f"🔍 Kontrol başladı: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if self.is_first_run:
            print(f"🎉 İLK ÇALIŞTIRMA - Mevcut versiyonlar taranıyor...")
            print(f"   Tüm bulunan pluginler Discord'a bildirilecek!")
        else:
            self.check_counter += 1
            print(f"🎯 Kontrol #{self.check_counter}")
        
        print(f"{'='*70}\n")
        
        all_updates = []
        
        # SpigotMC
        print("📦 SpigotMC kontrol ediliyor...")
        spigot_updates = self.check_spigot_updates()
        all_updates.extend(spigot_updates)
        print()
        
        # Modrinth
        print("🟢 Modrinth kontrol ediliyor...")
        modrinth_updates = self.check_modrinth_updates()
        all_updates.extend(modrinth_updates)
        print()
        
        # Polymart
        print("🟣 Polymart kontrol ediliyor...")
        polymart_updates = self.check_polymart_updates()
        all_updates.extend(polymart_updates)
        print()
        
        # GitHub
        print("⚫ GitHub kontrol ediliyor...")
        github_updates = self.check_github_updates()
        all_updates.extend(github_updates)
        print()
        
        # Discord'a bildir
        if all_updates:
            print(f"📤 Discord'a bildirimler gönderiliyor...")
            
            if self.is_first_run:
                print(f"   🎊 İlk çalıştırma - {len(all_updates)} plugin bildiriliyor!\n")
            else:
                print(f"   ✨ {len(all_updates)} yeni güncelleme bildiriliyor!\n")
            
            for i, update in enumerate(all_updates, 1):
                print(f"   [{i}/{len(all_updates)}] 📢 {update['name']} v{update['version']}")
                self.send_discord_notification(update)
                time.sleep(1.5)  # Discord rate limit
        
        # Kaydet
        self.save_seen_updates()
        
        # İlk çalıştırma tamamlandı
        if self.is_first_run:
            self.is_first_run = False
            print(f"\n{'='*70}")
            print(f"🎊 İlk çalıştırma tamamlandı!")
            print(f"   ✓ {len(self.tracked_plugins)} plugin tarandı")
            print(f"   ✓ {len(all_updates)} plugin Discord'a bildirildi")
            print(f"   ✓ Artık sadece YENİ güncellemeler bildirilecek")
            print(f"{'='*70}\n")
        else:
            print(f"\n{'='*70}")
            print(f"✅ Kontrol tamamlandı: {len(all_updates)} güncelleme bulundu")
            print(f"{'='*70}\n")
        
        return len(all_updates)

    def run(self, interval_minutes: int = 30):
        """Belirli aralıklarla kontrol et"""
        print("╔════════════════════════════════════════════════════════════╗")
        print("║         🤖 Minecraft Plugin Update Checker 🤖             ║")
        print("╚════════════════════════════════════════════════════════════╝")
        print(f"\n⚙️  Ayarlar:")
        print(f"   • Kontrol aralığı: {interval_minutes} dakika")
        print(f"   • Takip edilen plugin: {len(self.tracked_plugins)} adet")
        
        spigot_count = len([p for p in self.tracked_plugins.values() if 'spigot_id' in p])
        modrinth_count = len([p for p in self.tracked_plugins.values() if 'modrinth_slug' in p])
        polymart_count = len([p for p in self.tracked_plugins.values() if 'polymart_id' in p])
        github_count = len([p for p in self.tracked_plugins.values() if 'github_repo' in p])
        
        print(f"   • 🟠 SpigotMC: {spigot_count} | 🟢 Modrinth: {modrinth_count}")
        print(f"   • 🟣 Polymart: {polymart_count} | ⚫ GitHub: {github_count}")
        print(f"\n🚀 Bot başlatıldı! İlk kontrol yapılıyor...\n")
        
        while True:
            try:
                self.check_all_updates()
                
                print(f"⏰ Sonraki kontrol: {interval_minutes} dakika sonra")
                print(f"💤 Bekleniyor...\n")
                
                time.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                print("\n\n╔═══════════════════════════════════════╗")
                print("║   👋 Bot durduruldu! Görüşürüz!       ║")
                print("╚═══════════════════════════════════════╝\n")
                break
            except Exception as e:
                print(f"⚠ Beklenmeyen hata: {e}")
                print("⏳ 5 dakika sonra tekrar denenecek...\n")
                time.sleep(300)


if __name__ == "__main__":
    # Discord Webhook URL'iniz
    WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL') or "https://discord.com/api/webhooks/1465553053284307078/HJw7uPSX4G4jb1GkbRWkVFtsxHcWUX37KWvcfEoZm5XanHqw9gPAbeREpeNHUOPOcjOE"
    
    if not WEBHOOK_URL or WEBHOOK_URL == "BURAYA_WEBHOOK_URL_YAPISTIR":
        print("\n╔════════════════════════════════════════════════════════════╗")
        print("║              ⚠️  WEBHOOK URL EKSİK!                       ║")
        print("╚════════════════════════════════════════════════════════════╝\n")
        print("📋 Discord Webhook URL'i nasıl alınır:\n")
        print("   1️⃣  Discord sunucunuzda bir kanala gidin")
        print("   2️⃣  Kanal Ayarları → Entegrasyonlar → Webhook'lar")
        print("   3️⃣  'Yeni Webhook' butonuna tıklayın")
        print("   4️⃣  Webhook URL'ini kopyalayın")
        print("   5️⃣  Bu dosyada 63. satırı bulun:")
        print("       WEBHOOK_URL = \"WEBHOOK_URL_BURAYA\"")
        print("\n💡 Örnek webhook URL:")
        print("   https://discord.com/api/webhooks/123456789/abcdefgh...")
        print("\n" + "="*62)
        input("\n⏸️  Devam etmek için Enter'a basın...")
    else:
        try:
            print("\n🔍 Webhook URL kontrol ediliyor...")
            test_response = requests.post(
                WEBHOOK_URL, 
                json={"content": "✅ Webhook bağlantısı başarılı! Bot başlatılıyor..."},
                timeout=5
            )
            
            if test_response.status_code == 204:
                print("✅ Webhook URL geçerli!\n")
                checker = PluginUpdateChecker(WEBHOOK_URL)
                checker.run(interval_minutes=30)
            else:
                print(f"\n❌ HATA: Webhook URL geçersiz!")
                print(f"   HTTP Durum Kodu: {test_response.status_code}")
                print(f"   Yanıt: {test_response.text[:100]}")
                print("\n💡 Webhook URL'ini kontrol edin ve tekrar deneyin.\n")
                input("⏸️  Devam etmek için Enter'a basın...")
                
        except requests.exceptions.MissingSchema:
            print("\n❌ HATA: Webhook URL formatı yanlış!")
            print("   URL 'https://' ile başlamalı")
            print("\n💡 Doğru format:")
            print("   https://discord.com/api/webhooks/123456789/abcdefgh...\n")
            input("⏸️  Devam etmek için Enter'a basın...")
            
        except requests.exceptions.ConnectionError:
            print("\n❌ HATA: İnternet bağlantısı yok!")
            print("   Lütfen internet bağlantınızı kontrol edin.\n")
            input("⏸️  Devam etmek için Enter'a basın...")
