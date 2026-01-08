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
        self.check_counter = 0  # Kaç kez kontrol yapıldığını takip eder
        self.is_first_run = not os.path.exists(self.data_file)  # İlk çalıştırma mı?
        
        # Takip edilen plugin isimleri (büyük/küçük harf duyarsız)
        self.tracked_plugin_names = {
            # SpigotMC pluginleri
            "essentialsx", "vault", "luckperms", "worldedit", "worldguard",
            "multiverse-core", "protocollib", "placeholderapi", "gsit",
            "itemsadder", "litebans", "tab", "votifier", "advancedenchantments",
            "citizens", "discordsrv", "blueslimecore", "combatlogx", "essentials",
            "essentialsspawn", "eventbridge", "excellentcrates", "farmer",
            "fastasyncworldedit", "freedomchat", "illegalstack", "images",
            "infiniteannouncements", "interactivechat", "invseplusplus",
            "itemshider", "leaderos", "litlibs", "litminions", "lpc",
            "menus", "mycommand", "nbtmfi", "obtaskmanager", "dailyquests",
            "ofprotection", "packetevents", "playervault", "premiumads",
            "quickshop-hikari", "rankup", "realmines", "simpleportals",
            "ultimateautorestart", "viabackwards", "viaversion", "voicechat",
            "votingplugin", "vulcan", "xpbottle", "rosestacker",
            "economyshopgui", "geyser", "floodgate", "chunky",
            "advancedteleport", "antiafk", "autopickup", "abanseme",
            "discord", "advancedchests", "advancedorder", "advancementannouncer",
            "arblockerblocker", "allmesaj", "ajparkour", "antiheadstoneclock",
            "antisunger", "adflimiter", "bankmenu", "saesonalrankup",
            "alestesi", "altascoin", "atlaslauncher", "atlasmoderation",
            "evoterparty", "axfunctions", "axinventoryrestore", "axnewards",
            "axtrade", "banitem", "battlepasses", "bentobox", "bentobox-bank",
            "bentobox-border", "bentobox-bskyblock", "bentobox-chat",
            "bentobox-level", "bentobox-limits", "bentobox-biomes",
            "chatgentry", "citizens", "clearlag", "commandmanager",
            "crazycrvous", "decentholograms", "deluxemenus", "donutoorder",
            "duels", "elevator", "eventbridge", "excellentcrates",
            "farmer", "fastasyncworldedit", "freedomchat", "gsit",
            "illegalstack", "images", "infiniteannouncements", "interactivechat",
            "invseeplysplus", "itemshider", "leaderos", "litebans",
            "litlibs", "litminions", "lpc", "luckperms", "menus",
            "multiverse-core", "mycommand", "nbtmfi", "obtaskmanager",
            "dailyquests", "ofprotection", "packetevents", "placeholderapi",
            "playervault", "premiumads", "protocollib", "quickshop-hikari",
            "rankup", "realmines", "simpleportals", "tab",
            "ultimateautorestart", "vault", "viabackwards", "viaversion",
            "voicechat", "votifier", "votingplugin", "vulcan",
            "worldguard", "xpbottle", "coreprotect", "dynmap", "mythicmobs",
        }
        
        # GitHub'da takip edilecek repository'ler (owner/repo formatında)
        self.github_repos = [
            "EssentialsX/Essentials",
            "LuckPerms/LuckPerms",
            "EngineHub/WorldEdit",
            "EngineHub/WorldGuard",
            "PlaceholderAPI/PlaceholderAPI",
            "dmulloy2/ProtocolLib",
            "GeyserMC/Geyser",
            "GeyserMC/Floodgate",
            "ViaVersion/ViaVersion",
            "ViaVersion/ViaBackwards",
            "MilkBowl/Vault",
            "CitizensDev/Citizens2",
            "DiscordSRV/DiscordSRV",
            # Daha fazla ekleyebilirsiniz
        ]

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

    def normalize_name(self, name: str) -> str:
        """Plugin ismini normalize et (karşılaştırma için)"""
        normalized = re.sub(r'[^a-z0-9]', '', name.lower())
        return normalized

    def is_tracked_plugin(self, plugin_name: str) -> bool:
        """Bu plugin takip ediliyor mu?"""
        normalized = self.normalize_name(plugin_name)
        
        if normalized in self.tracked_plugin_names:
            return True
        
        for tracked in self.tracked_plugin_names:
            if tracked in normalized or normalized in tracked:
                return True
        
        return False

    def should_check_all_plugins(self) -> bool:
        """Her zaman sadece takip edilen pluginleri kontrol et"""
        self.check_counter += 1
        return False  # Artık hiçbir zaman tüm pluginleri kontrol etme

    def check_spigot_recent_updates(self, check_all: bool = False) -> List[Dict]:
        """SpigotMC'deki son güncellemeleri kontrol et (Spiget API)"""
        updates = []
        
        try:
            print(f"   📡 SpigotMC (Spiget API) sorgulanıyor...")
            
            api_url = "https://api.spiget.org/v2/resources?size=100&sort=-updateDate"
            response = requests.get(api_url, timeout=15)
            
            if response.status_code == 200:
                resources = response.json()
                
                checked = 0
                found_tracked = 0
                
                for resource in resources:
                    plugin_name = resource.get('name', '')
                    resource_id = str(resource.get('id', ''))
                    
                    checked += 1
                    
                    # Sadece takip edilen pluginleri kontrol et
                    if self.is_tracked_plugin(plugin_name):
                        found_tracked += 1
                        
                        version_info = self.get_spigot_version(resource_id)
                        if version_info:
                            update_key = f"spigot_{resource_id}_{version_info['version']}"
                            
                            if update_key not in self.seen_updates:
                                self.seen_updates[update_key] = datetime.now(timezone.utc).isoformat()
                                
                                updates.append({
                                    "name": plugin_name,
                                    "platform": "SpigotMC",
                                    "version": version_info['version'],
                                    "url": f"https://www.spigotmc.org/resources/{resource_id}/",
                                    "color": 16753920,  # Turuncu
                                    "resource_id": resource_id,
                                })
                                
                                print(f"   ✓ Yeni güncelleme: {plugin_name} v{version_info['version']}")
                        
                        time.sleep(0.2)
                
                print(f"   → {checked} plugin kontrol edildi, {found_tracked} takip edilen bulundu")
                
            else:
                print(f"   ✗ Spiget API hatası: Status {response.status_code}")
                
        except Exception as e:
            print(f"   ✗ SpigotMC kontrol hatası: {e}")
        
        return updates

    def get_spigot_version(self, resource_id: str) -> Optional[Dict]:
        """Spigot plugin versiyonunu al"""
        try:
            url = f"https://api.spiget.org/v2/resources/{resource_id}/versions/latest"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {"version": data.get('name', 'Unknown')}
        except:
            pass
        return None

    def check_modrinth_recent_updates(self, check_all: bool = False) -> List[Dict]:
        """Modrinth'deki son güncellemeleri kontrol et"""
        updates = []
        
        try:
            print(f"   📡 Modrinth API sorgulanıyor...")
            
            url = "https://api.modrinth.com/v2/search"
            params = {
                "facets": '[["project_type:plugin"]]',
                "index": "updated",
                "limit": 50,
            }
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                for project in data.get('hits', []):
                    plugin_name = project.get('title', '')
                    slug = project.get('slug', '')
                    
                    if self.is_tracked_plugin(plugin_name):
                        versions_url = f"https://api.modrinth.com/v2/project/{slug}/version"
                        versions_response = requests.get(versions_url, timeout=10)
                        
                        if versions_response.status_code == 200:
                            versions = versions_response.json()
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
                                        "color": 1752220,  # Yeşil
                                        "changelog": latest.get('changelog', '')[:200],
                                    })
                                    
                                    print(f"   ✓ Yeni güncelleme: {plugin_name} v{version}")
                        
                        time.sleep(0.3)
                
        except Exception as e:
            print(f"   ✗ Modrinth hatası: {e}")
        
        return updates

    def check_polymart_recent_updates(self, check_all: bool = False) -> List[Dict]:
        """Polymart'daki son güncellemeleri kontrol et"""
        updates = []
        
        try:
            print(f"   📡 Polymart API sorgulanıyor...")
            
            # Polymart API v1 endpoint
            url = "https://api.polymart.org/v1/getResources"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            params = {
                "sort": "date_updated",
                "per_page": 50,
                "page": 1
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=15)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    resources = data.get('response', {}).get('resources', [])
                    
                    if resources:
                        for resource in resources[:50]:  # İlk 50 tane
                            plugin_name = resource.get('title', '')
                            resource_id = str(resource.get('resource_id', ''))
                            version = resource.get('version', 'Unknown')
                            
                            if self.is_tracked_plugin(plugin_name):
                                update_key = f"polymart_{resource_id}_{version}"
                                
                                if update_key not in self.seen_updates:
                                    self.seen_updates[update_key] = datetime.now(timezone.utc).isoformat()
                                    
                                    updates.append({
                                        "name": plugin_name,
                                        "platform": "Polymart",
                                        "version": version,
                                        "url": f"https://polymart.org/resource/{resource_id}",
                                        "color": 15418782,  # Pembe
                                    })
                                    
                                    print(f"   ✓ Yeni güncelleme: {plugin_name} v{version}")
                    else:
                        print(f"   ⚠ Polymart'tan veri alınamadı (boş yanıt)")
                except json.JSONDecodeError:
                    print(f"   ⚠ Polymart API yanıtı okunamadı (JSON hatası)")
            else:
                print(f"   ⚠ Polymart API erişilemiyor (Status: {response.status_code})")
                
        except requests.exceptions.Timeout:
            print(f"   ⚠ Polymart API zaman aşımı")
        except Exception as e:
            print(f"   ⚠ Polymart şu an kullanılamıyor: {e}")
        
        return updates

    def check_builtbybit_recent_updates(self, check_all: bool = False) -> List[Dict]:
        """BuiltByBit'deki son güncellemeleri kontrol et"""
        updates = []
        
        try:
            print(f"   📡 BuiltByBit API sorgulanıyor...")
            
            # BuiltByBit API v1 (eski MC-Market)
            url = "https://api.builtbybit.com/v1/resources"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            params = {
                "sort": "-last_update",
                "size": 50
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=15)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    resources = data.get('data', [])
                    
                    if resources:
                        for resource in resources:
                            plugin_name = resource.get('title', '')
                            resource_id = str(resource.get('id', ''))
                            
                            # Version bilgisi farklı yerlerde olabilir
                            version_data = resource.get('current_version', {})
                            if isinstance(version_data, dict):
                                version = version_data.get('name', 'Unknown')
                            else:
                                version = str(version_data) if version_data else 'Unknown'
                            
                            if self.is_tracked_plugin(plugin_name):
                                update_key = f"builtbybit_{resource_id}_{version}"
                                
                                if update_key not in self.seen_updates:
                                    self.seen_updates[update_key] = datetime.now(timezone.utc).isoformat()
                                    
                                    updates.append({
                                        "name": plugin_name,
                                        "platform": "BuiltByBit",
                                        "version": version,
                                        "url": f"https://builtbybit.com/resources/{resource_id}/",
                                        "color": 3066993,  # Koyu yeşil
                                    })
                                    
                                    print(f"   ✓ Yeni güncelleme: {plugin_name} v{version}")
                    else:
                        print(f"   ⚠ BuiltByBit'ten veri alınamadı (boş yanıt)")
                except json.JSONDecodeError:
                    print(f"   ⚠ BuiltByBit API yanıtı okunamadı (JSON hatası)")
            else:
                print(f"   ⚠ BuiltByBit API erişilemiyor (Status: {response.status_code})")
                
        except requests.exceptions.Timeout:
            print(f"   ⚠ BuiltByBit API zaman aşımı")
        except Exception as e:
            print(f"   ⚠ BuiltByBit şu an kullanılamıyor: {e}")
        
        return updates

    def check_github_releases(self) -> List[Dict]:
        """GitHub'daki yeni release'leri kontrol et"""
        updates = []
        
        try:
            print(f"   📡 GitHub API sorgulanıyor... ({len(self.github_repos)} repo)")
            
            for repo in self.github_repos:
                try:
                    url = f"https://api.github.com/repos/{repo}/releases/latest"
                    headers = {"Accept": "application/vnd.github.v3+json"}
                    
                    response = requests.get(url, headers=headers, timeout=10)
                    
                    if response.status_code == 200:
                        release = response.json()
                        
                        tag_name = release.get('tag_name', 'Unknown')
                        name = release.get('name', repo.split('/')[1])
                        published_at = release.get('published_at', '')
                        
                        update_key = f"github_{repo}_{tag_name}"
                        
                        if update_key not in self.seen_updates:
                            self.seen_updates[update_key] = datetime.now(timezone.utc).isoformat()
                            
                            updates.append({
                                "name": name,
                                "platform": "GitHub",
                                "version": tag_name,
                                "url": release.get('html_url', f"https://github.com/{repo}"),
                                "color": 2303786,  # GitHub siyahı
                                "changelog": release.get('body', '')[:200],
                            })
                            
                            print(f"   ✓ Yeni release: {name} {tag_name}")
                    
                    time.sleep(0.5)  # GitHub rate limit
                    
                except Exception as e:
                    print(f"   ✗ {repo} hatası: {e}")
                
        except Exception as e:
            print(f"   ✗ GitHub kontrol hatası: {e}")
        
        return updates

    def send_discord_notification(self, update_info: Dict):
        """Discord'a güncelleme bildirimi gönder"""
        
        fields = [
            {
                "name": "✨ Versiyon",
                "value": f"`{update_info['version']}`",
                "inline": True
            },
            {
                "name": "📦 Platform",
                "value": update_info['platform'],
                "inline": True
            }
        ]
        
        if update_info.get('changelog') and update_info['changelog'].strip():
            changelog = update_info['changelog'][:200]
            if len(update_info['changelog']) > 200:
                changelog += "..."
            fields.append({
                "name": "📝 Değişiklikler",
                "value": changelog,
                "inline": False
            })
        
        fields.append({
            "name": "🔗 İndir",
            "value": f"[Buraya tıkla]({update_info['url']})",
            "inline": False
        })
        
        embed = {
            "title": f"🔔 {update_info['name']} Güncellendi!",
            "description": f"Yeni bir versiyon yayınlandı!",
            "color": update_info['color'],
            "fields": fields,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "footer": {
                "text": "Plugin Update Checker"
            }
        }

        payload = {
            "username": "Plugin Update Bot",
            "embeds": [embed]
        }

        try:
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            if response.status_code == 204:
                print(f"      ✓ Discord bildirimi gönderildi")
            else:
                print(f"      ✗ Discord hatası: {response.status_code}")
        except Exception as e:
            print(f"      ✗ Discord gönderim hatası: {e}")

    def check_all_updates(self):
        """Tüm platformlardaki güncellemeleri kontrol et"""
        print(f"\n{'='*70}")
        print(f"🔍 Kontrol başladı: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if self.is_first_run:
            print(f"🎉 İLK ÇALIŞTIRMA - TAKİP EDİLEN PLUGİNLER AKTARILIYOR!")
        else:
            print(f"🎯 Kontrol #{self.check_counter + 1} - Takip Edilen Pluginler")
        
        print(f"{'='*70}\n")
        
        all_updates = []
        
        # SpigotMC
        print("📦 SpigotMC kontrol ediliyor...")
        spigot_updates = self.check_spigot_recent_updates()
        all_updates.extend(spigot_updates)
        print(f"   → {len(spigot_updates)} yeni güncelleme\n")
        
        # Modrinth
        print("🟢 Modrinth kontrol ediliyor...")
        modrinth_updates = self.check_modrinth_recent_updates()
        all_updates.extend(modrinth_updates)
        print(f"   → {len(modrinth_updates)} yeni güncelleme\n")
        
        # Polymart - ŞİMDİLİK DEVRE DIŞI (API çalışmıyor)
        # print("🟣 Polymart kontrol ediliyor...")
        # polymart_updates = self.check_polymart_recent_updates()
        # all_updates.extend(polymart_updates)
        # print(f"   → {len(polymart_updates)} yeni güncelleme\n")
        
        # BuiltByBit - ŞİMDİLİK DEVRE DIŞI (API çalışmıyor)
        # print("🟤 BuiltByBit kontrol ediliyor...")
        # builtbybit_updates = self.check_builtbybit_recent_updates()
        # all_updates.extend(builtbybit_updates)
        # print(f"   → {len(builtbybit_updates)} yeni güncelleme\n")
        
        # GitHub (sadece takip edilenler)
        print("⚫ GitHub kontrol ediliyor...")
        github_updates = self.check_github_releases()
        all_updates.extend(github_updates)
        print(f"   → {len(github_updates)} yeni güncelleme\n")
        
        # Discord'a bildir
        if all_updates:
            print(f"📤 Discord'a bildirimler gönderiliyor...\n")
            for update in all_updates:
                print(f"   📢 {update['name']} v{update['version']}")
                self.send_discord_notification(update)
                time.sleep(1)  # Discord rate limit
        
        # Kaydet
        self.save_seen_updates()
        
        # İlk çalıştırmayı tamamladık
        if self.is_first_run:
            self.is_first_run = False
            print(f"\n🎊 İlk çalıştırma tamamlandı! Artık sadece YENİ güncellemeler bildirilecek.")
        
        print(f"\n{'='*70}")
        print(f"✅ Kontrol tamamlandı: {len(all_updates)} toplam güncelleme")
        print(f"{'='*70}\n")
        
        return len(all_updates)

    def run(self, interval_minutes: int = 30):
        """Belirli aralıklarla kontrol et"""
        print("╔═══════════════════════════════════════════════════════════╗")
        print("║         🤖 Minecraft Plugin Update Checker 🤖             ║")
        print("╚═══════════════════════════════════════════════════════════╝")
        print(f"\n⚙️  Ayarlar:")
        print(f"   • Kontrol aralığı: {interval_minutes} dakika")
        print(f"   • Takip edilen plugin: {len(self.tracked_plugin_names)} adet")
        print(f"   • GitHub repos: {len(self.github_repos)} adet")
        print(f"   • Aktif platformlar: SpigotMC, Modrinth, GitHub")
        print(f"   • Not: Polymart ve BuiltByBit public API'leri mevcut değil")
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
    # Environment variable'dan veya doğrudan koddan webhook al
    WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL') or "https://discord.com/api/webhooks/1458675898650984539/La_MIQTt0PUo55J4cCWqSBnn2jKizh5pucXvVMt73k1kH-tACIpMpJzzDz1Fdz-aLiK5"
    
    if not WEBHOOK_URL or WEBHOOK_URL == "BURAYA_WEBHOOK_URL_YAPISTIR":
        print("\n⚠ HATA: Discord Webhook URL'i ayarlanmamış!\n")
        print("📋 Webhook nasıl alınır:")
        print("   1. Discord sunucunda bir kanala git")
        print("   2. Kanal Ayarları → Entegrasyonlar → Webhook'lar")
        print("   3. 'Yeni Webhook' butonuna tıkla")
        print("   4. Webhook URL'ini kopyala")
        print("   5. Render.com'da Environment Variables'a ekle\n")
    else:
        checker = PluginUpdateChecker(WEBHOOK_URL)
        checker.run(interval_minutes=30)  # Her 30 dakikada kontrol et