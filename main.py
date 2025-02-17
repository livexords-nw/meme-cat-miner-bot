from datetime import datetime
import json
import time
from colorama import Fore
import requests

class memeCatMiner:
    BASE_URL = "https://revelationwithai.com/service1/"
    HEADERS = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-GB,en;q=0.9,en-US;q=0.8",
        "content-type": "application/json",
        "origin": "https://revelationwithai.com",
        "priority": "u=1, i",
        "sec-ch-ua": '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24", "Microsoft Edge WebView2";v="131"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0" 
    }

    def __init__(self):
        self.query_list = self.load_query("query.txt")
        self.token = None
        self.coins = 0
        self.level = 0
        self.mine_capacity = 0
        self.claimed_lootboxes = 0

    def banner(self) -> None:
        """Displays the banner for the bot."""
        self.log("🎉 Meme Cat Miner Free Bot", Fore.CYAN)
        self.log("🚀 Created by LIVEXORDS", Fore.CYAN)
        self.log("📢 Channel: t.me/livexordsscript\n", Fore.CYAN)

    def log(self, message, color=Fore.RESET):
            print(Fore.LIGHTBLACK_EX + datetime.now().strftime("[%Y:%m:%d ~ %H:%M:%S] |") + " " + color + message + Fore.RESET)

    def load_config(self) -> dict:
        """
        Loads configuration from config.json.

        Returns:
            dict: Configuration data or an empty dictionary if an error occurs.
        """
        try:
            with open("config.json", "r") as config_file:
                config = json.load(config_file)
                self.log("✅ Configuration loaded successfully.", Fore.GREEN)
                return config
        except FileNotFoundError:
            self.log("❌ File not found: config.json", Fore.RED)
            return {}
        except json.JSONDecodeError:
            self.log("❌ Failed to parse config.json. Please check the file format.", Fore.RED)
            return {}

    def load_query(self, path_file: str = "query.txt") -> list:
        """
        Loads a list of queries from the specified file.

        Args:
            path_file (str): The path to the query file. Defaults to "query.txt".

        Returns:
            list: A list of valid queries or an empty list if an error occurs.
        """
        self.banner()

        try:
            with open(path_file, "r", encoding="utf-8") as file: 
                queries = [line.strip() for line in file if line.strip()]

            if not queries:
                self.log(f"⚠️ Warning: {path_file} is empty.", Fore.YELLOW)
                return []

            valid_queries = []
            for query in queries:
                if "|" in query:
                    valid_queries.append(query)
                else:
                    self.log(f"⚠️ Invalid query format skipped: {query}", Fore.YELLOW)

            if not valid_queries:
                self.log(f"⚠️ No valid queries found in {path_file}.", Fore.YELLOW)
                return []

            self.log(f"✅ Loaded {len(valid_queries)} valid queries from {path_file}.", Fore.GREEN)
            return valid_queries

        except FileNotFoundError:
            self.log(f"❌ File not found: {path_file}", Fore.RED)
            return []
        except UnicodeDecodeError:
            self.log(f"❌ Unable to read file (encoding issue): {path_file}", Fore.RED)
            return []
        except Exception as e:
            self.log(f"❌ Unexpected error loading queries: {e}", Fore.RED)
            return []

    def login(self, index: int) -> None:
        self.log("🔒 Attempting to log in...", Fore.GREEN)

        if index >= len(self.query_list):
            self.log("❌ Invalid login index. Please check again.", Fore.RED)
            return

        raw_token = self.query_list[index]
        try:
            telegram_id, user_name = raw_token.split("|")
        except ValueError:
            self.log("❌ Token format is invalid. Expected format: id|username.", Fore.RED)
            return

        req_url = f"{self.BASE_URL}player/login"
        payload = {
            "telegram_id": telegram_id,
            "user_name": user_name,
        }

        hidden_telegram_id = f"{telegram_id[:4]}****"
        hidden_user_name = f"{user_name[:3]}***"
        self.log(f"📋 Using payload: telegram id={hidden_telegram_id}, user name={hidden_user_name}", Fore.CYAN)

        headers = {**self.HEADERS}

        try:
            self.log("📡 Sending POST request to log in...", Fore.CYAN)
            response = requests.post(req_url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

            if data.get("code") == 200:
                result = data.get("result", {})
                self.token = result.get("token", None)

                if self.token:
                    self.log("🔑 Login successful! Token retrieved.", Fore.GREEN)
                else:
                    self.log("⚠️ Token not found in response.", Fore.YELLOW)

                self.update_info()
                
            else:
                self.log(f"⚠️ Login failed. Message: {data.get('msg', 'Unknown error')}", Fore.YELLOW)

        except requests.exceptions.RequestException as e:
            self.log(f"❌ Failed to send login request: {e}", Fore.RED)
            if response:
                self.log(f"📄 Response content: {response.text}", Fore.RED)
        except ValueError as e:
            self.log(f"❌ Data error (possible JSON issue): {e}", Fore.RED)
            if response:
                self.log(f"📄 Response content: {response.text}", Fore.RED)
        except Exception as e:
            self.log(f"❌ Unexpected error: {e}", Fore.RED)
            if response:
                self.log(f"📄 Response content: {response.text}", Fore.RED)

    def update_info(self) -> dict:
        """
        Updates the user's information from the server.

        Returns:
            dict: A dictionary containing the user's updated information, or an empty dict if an error occurs.
        """
        req_url_info = f"{self.BASE_URL}player/info"
        headers = {**self.HEADERS, "authorization": self.token}

        try:
            self.log("📡 Fetching updated player info...", Fore.CYAN)
            response = requests.get(req_url_info, headers=headers)
            response.raise_for_status()

            info_data = response.json()

            if info_data.get("code") != 200:
                self.log(f"⚠️ Failed to fetch player info: {info_data.get('msg', 'Unknown error')}", Fore.YELLOW)
                return {}

            result = info_data.get("result", {})
            if not result:
                self.log("⚠️ Missing 'result' field in response.", Fore.YELLOW)
                return {}

            self.token = result.get("token", self.token) 
            self.coins = int(float(result.get("coins", 0)))
            name = result.get("name", "Unknown")
            self.level = result.get("level", 0)
            rank = result.get("level_info", {}).get("rank", "Unknown")
            avatar = result.get("avatar", "")
            self.mine_capacity = result.get("mine_capacity", "")
            self.claimed_lootboxes = result.get("claimed_lootboxes", "")

            self.log("✅ Player info updated successfully!", Fore.GREEN)
            self.log(f"👤 Name: {name}", Fore.LIGHTGREEN_EX)
            self.log(f"💎 Coins: {self.coins}", Fore.CYAN)
            self.log(f"🎖️ Level: {self.level} ({rank})", Fore.LIGHTBLUE_EX)

            return {
                "name": name,
                "coins": self.coins,
                "level": self.level,
                "rank": rank,
                "avatar": avatar,
                "token": self.token,
            }

        except requests.exceptions.RequestException as e:
            self.log(f"❌ Failed to fetch player info: {e}", Fore.RED)
            if response:
                self.log(f"📄 Response content: {response.text}", Fore.RED)
            return {}
        except ValueError as e:
            self.log(f"❌ Data error: {e}", Fore.RED)
            if response:
                self.log(f"📄 Response content: {response.text}", Fore.RED)
            return {}
        except Exception as e:
            self.log(f"❌ An unexpected error occurred: {e}", Fore.RED)
            if response:
                self.log(f"📄 Response content: {response.text}", Fore.RED)
            return {}

    def task(self):
        """
        Handles task-related operations, including listing tasks, completing tasks, performing daily check-in,
        claiming lootbox rewards, and claiming invite lootboxes.

        Returns:
            dict: A dictionary summarizing the task status and rewards collected.
        """
        headers = {**self.HEADERS, "authorization": self.token}
        summary = {"completed_tasks": [], "checkin_reward": 0}

        # Step 1: Fetch task list
        try:
            self.log("📡 Fetching task list...", Fore.CYAN)
            task_list_url = f"{self.BASE_URL}task/list"
            response = requests.get(task_list_url, headers=headers)
            response.raise_for_status()

            task_data = response.json()
            if task_data.get("code") != 200:
                self.log(f"⚠️ Failed to fetch task list: {task_data.get('msg', 'Unknown error')}", Fore.YELLOW)
                return summary

            tasks = task_data.get("result", {}).get("tasks", {})
            daily_task = tasks.get("daily_task", [])
            task_list = tasks.get("task_list", [])

            # Log tasks
            self.log("✅ Task list retrieved successfully!", Fore.GREEN)
            for task in daily_task + task_list:
                self.log(f"📝 Task: {task['name']} - Reward: {task['reward']['coins']} coins", Fore.LIGHTBLUE_EX)

            # Step 2: Perform daily check-in
            self.log("📡 Performing daily check-in...", Fore.CYAN)
            checkin_url = f"{self.BASE_URL}checkin"
            response = requests.post(checkin_url, headers=headers)
            response.raise_for_status()

            checkin_data = response.json()
            if checkin_data.get("code") == 200:
                reward = checkin_data["result"]["reward"]["coins"]
                summary["checkin_reward"] = reward
                self.log(f"✅ Check-in successful! Reward: {reward} coins", Fore.GREEN)
            else:
                self.log(f"⚠️ Check-in failed: {checkin_data.get('msg', 'Unknown error')}", Fore.YELLOW)

            # Step 3: Complete available tasks
            for task in task_list:
                if not task["is_completed"]:
                    task_id = task["id"]
                    complete_url = f"{self.BASE_URL}task/complete?task_id={task_id}"

                    self.log(f"📡 Completing task: {task['name']}...", Fore.CYAN)
                    response = requests.post(complete_url, headers=headers, json={"task_id": task_id})
                    response.raise_for_status()

                    complete_data = response.json()
                    if complete_data.get("code") == 200:
                        reward = complete_data["result"]["reward"]["coins"]
                        summary["completed_tasks"].append({"task_id": task_id, "reward": reward})
                        self.log(f"✅ Task '{task['name']}' completed! Reward: {reward} coins", Fore.GREEN)
                    else:
                        self.log(f"⚠️ Failed to complete task '{task['name']}': {complete_data.get('msg', 'Unknown error')}", Fore.YELLOW)

            # New Step 4: Claim lootbox rewards after completing tasks.
            self.log("📡 Claiming lootbox rewards...", Fore.CYAN)
            lootbox_url = f"{self.BASE_URL}task/claim_lootbox"
            lootbox_response = requests.post(lootbox_url, headers=headers)
            lootbox_response.raise_for_status()
            lootbox_data = lootbox_response.json()
            if lootbox_data.get("code") == 200:
                claimed_lootboxes = lootbox_data.get("result", {}).get("claimed_lootboxes", 0)
                new_unclaimed_lootboxes = lootbox_data.get("result", {}).get("new_unclaimed_lootboxes", 0)
                summary["lootbox_claim"] = {
                    "claimed_lootboxes": claimed_lootboxes,
                    "new_unclaimed_lootboxes": new_unclaimed_lootboxes
                }
                self.log(f"✅ Successfully claimed lootboxes: {claimed_lootboxes} claimed, {new_unclaimed_lootboxes} new unclaimed.", Fore.GREEN)
            else:
                self.log(f"⚠️ Failed to claim lootboxes: {lootbox_data.get('msg', 'Unknown error')}", Fore.YELLOW)

            # New Step 5: Claim invite lootboxes.
            self.log("📡 Claiming invite lootboxes...", Fore.CYAN)
            invite_lootbox_url = f"{self.BASE_URL}invite/claim_lootboxes"
            invite_lootbox_response = requests.post(invite_lootbox_url, headers=headers)
            invite_lootbox_response.raise_for_status()
            invite_lootbox_data = invite_lootbox_response.json()
            if invite_lootbox_data.get("code") == 200:
                claimed_invite_lootboxes = invite_lootbox_data.get("result", {}).get("claimed_lootboxes", 0)
                summary["invite_lootbox_claim"] = {"claimed_lootboxes": claimed_invite_lootboxes}
                self.log(f"✅ Successfully claimed invite lootboxes: {claimed_invite_lootboxes}", Fore.GREEN)
            else:
                self.log(f"⚠️ Failed to claim invite lootboxes: {invite_lootbox_data.get('msg', 'Unknown error')}", Fore.YELLOW)

        except requests.exceptions.RequestException as e:
            self.log(f"❌ Task operation failed: {e}", Fore.RED)
            return summary
        except Exception as e:
            self.log(f"❌ An unexpected error occurred: {e}", Fore.RED)
            return summary

        return summary

    def cat(self):
        """
        Mengambil daftar kucing dari API dan mencoba membeli kucing termahal yang memiliki properti `can_buy`.
        Meskipun pengguna mungkin kekurangan koin, tetap mencoba melakukan pembelian.
        
        Returns:
            dict: Dictionary yang berisi hasil operasi pembelian.
        """
        try:
            headers = {"Authorization": self.token}

            # Step 1: Fetch cat list
            self.log("📡 Fetching cat list...", Fore.CYAN)
            cat_list_url = f"{self.BASE_URL}store/catList"
            response = requests.get(cat_list_url, headers=headers)
            response.raise_for_status()

            cat_data = response.json()
            if cat_data.get("code") != 200:
                self.log(f"⚠️ Failed to fetch cat list: {cat_data.get('msg', 'Unknown error')}", Fore.YELLOW)
                return {"status": "error", "msg": "Failed to fetch cat list"}

            cats = cat_data.get("result", {}).get("cat_list", [])
            self.log("✅ Cat list retrieved successfully!", Fore.GREEN)

            # Step 2: Update user info (misalnya koin dan level)
            self.update_info()
            self.coins = int(self.coins)

            # Filter kucing yang memiliki properti 'can_buy' = True
            available_cats = [cat for cat in cats if cat.get('can_buy')]

            if not available_cats:
                self.log("❌ No cats available for purchase.", Fore.RED)
                return {"status": "error", "msg": "No cats could be purchased."}

            # Urutkan berdasarkan harga secara menurun dan ambil kucing paling mahal
            available_cats.sort(key=lambda cat: cat['price'], reverse=True)
            chosen_cat = available_cats[0]

            self.log(f"📡 Attempting to buy {chosen_cat['name']} for {chosen_cat['price']} coins...", Fore.CYAN)
            buy_cat_url = f"{self.BASE_URL}store/buyCat?breed_id={chosen_cat['breed_id']}"
            payload = {"breed_id": chosen_cat['breed_id']}
            response = requests.post(buy_cat_url, headers=headers, json=payload)
            response.raise_for_status()

            buy_data = response.json()
            if buy_data.get("code") == 200:
                self.log(f"✅ Successfully purchased {chosen_cat['name']}!", Fore.GREEN)
                # Kurangi coins meskipun kemungkinan pembelian gagal karena koin kurang
                self.coins -= chosen_cat['price']
                return {"status": "success", "purchased_cats": [chosen_cat['name']]}
            else:
                self.log(f"⚠️ Failed to purchase {chosen_cat['name']}: {buy_data.get('msg', 'Unknown error')}", Fore.YELLOW)
                return {"status": "error", "msg": f"Failed to purchase {chosen_cat['name']}: {buy_data.get('msg', 'Unknown error')}"}

        except requests.exceptions.RequestException as e:
            self.log(f"❌ Request failed: {e}", Fore.RED)
            return {"status": "error", "msg": f"Request failed: {e}"}
        except Exception as e:
            self.log(f"❌ An unexpected error occurred: {e}", Fore.RED)
            return {"status": "error", "msg": f"An unexpected error occurred: {e}"}

    def mining(self):
        """
        Menangani operasi penambangan untuk kucing milik pengguna dengan urutan:
        1. List current mining cats.
        2. Klaim hasil tambang untuk tiap cat yang sedang "working".
        3. List ulang current mining cats.
        4. End (remove) tiap cat dari tambang dengan API mine/end.
        5. Jika saat listing jumlah cat sudah mencapai self.mine_capacity,
        atau jika ada cat yang gagal di-ending, maka proses deploy tidak dilakukan.
        6. Jika memungkinkan (slot tersedia), beli slot baru dan ambil daftar cat user,
        filter dan pilih cat terbaik berdasarkan profitabilitas.
        7. Deploy cat-cat tersebut hingga mine_capacity terpenuhi.
        8. Start mining untuk cat-cat yang telah di-deploy (jika belum "working").
        9. Klik semua cat yang dideploy untuk bonus coin.

        Returns:
            dict: Ringkasan status operasi penambangan.
        """
        try:
            headers = {"Authorization": self.token}
            mining_summary = {
                "claimed": [],
                "ended": [],
                "deployed": [],
                "started": [],
                "clicked": []  # Mengubah menjadi list untuk menyimpan hasil click tiap cat
            }

            # === Step 1: List current mining cats ===
            self.log("📡 Fetching current mining cats...", Fore.CYAN)
            current_url = f"{self.BASE_URL}mine/current"
            try:
                current_response = requests.get(current_url, headers=headers)
                current_response.raise_for_status()
                current_data = current_response.json()
            except Exception as e:
                self.log(f"⚠️ Failed to fetch current mining cats: {e}", Fore.YELLOW)
                current_data = {}
            mining_cats = []
            if current_data.get("code") == 200:
                mining_cats = current_data.get("result", {}).get("mining_cats", [])
                self.log("✅ Current mining cats retrieved successfully!", Fore.GREEN)
            else:
                self.log("⚠️ No valid data for current mining cats.", Fore.YELLOW)

            initial_mining_count = len(mining_cats)
            # Jika jumlah cat yang sedang mining sudah mencapai kapasitas maksimal,
            # maka tidak usah melanjutkan ke deployment.
            if initial_mining_count == self.mine_capacity:
                self.log("⚠️ Mine capacity is full. Skipping deployment.", Fore.YELLOW)
                return {"status": "success", "mining_summary": mining_summary}

            # === Step 2: Klaim hasil tambang untuk tiap cat yang sedang 'working' ===
            for mcat in mining_cats:
                if mcat.get("stage", "").lower() == "working":
                    mcat_id = mcat.get("cat_id")
                    mcat_name = mcat.get("name", "Unknown")
                    self.log(f"📡 Claiming earnings for {mcat_name}...", Fore.CYAN)
                    try:
                        collect_url = f"{self.BASE_URL}mine/collect?cat_id={mcat_id}"
                        collect_payload = {"cat_id": mcat_id}
                        collect_response = requests.post(collect_url, headers=headers, json=collect_payload)
                        collect_response.raise_for_status()
                        collect_data = collect_response.json()
                        if collect_data.get("code") == 200:
                            earnings = collect_data.get("result", {}).get("earnings", 0)
                            self.log(f"✅ {mcat_name} collected {earnings} earnings successfully!", Fore.GREEN)
                            mining_summary["claimed"].append(mcat_name)
                        else:
                            self.log(f"⚠️ Failed to claim earnings for {mcat_name}: {collect_data.get('msg', 'Unknown error')}", Fore.YELLOW)
                    except Exception as e:
                        self.log(f"⚠️ Exception claiming earnings for {mcat_name}: {e}", Fore.YELLOW)

            # === Step 3: Re-fetch current mining cats untuk proses end ===
            self.log("📡 Re-fetching current mining cats for removal...", Fore.CYAN)
            try:
                current_response = requests.get(current_url, headers=headers)
                current_response.raise_for_status()
                current_data = current_response.json()
            except Exception as e:
                self.log(f"⚠️ Failed to re-fetch current mining cats: {e}", Fore.YELLOW)
                current_data = {}
            mining_cats = []
            if current_data.get("code") == 200:
                mining_cats = current_data.get("result", {}).get("mining_cats", [])

            # === Step 4: End (remove) tiap cat dari tambang ===
            ended_count = 0
            for mcat in mining_cats:
                mcat_id = mcat.get("cat_id")
                mcat_name = mcat.get("name", "Unknown")
                self.log(f"📡 Ending mining for {mcat_name}...", Fore.CYAN)
                try:
                    end_url = f"{self.BASE_URL}mine/end?cat_id={mcat_id}"
                    end_response = requests.post(end_url, headers=headers)
                    end_response.raise_for_status()
                    end_data = end_response.json()
                    if end_data.get("code") == 200:
                        self.log(f"✅ {mcat_name} ended mining successfully!", Fore.GREEN)
                        mining_summary["ended"].append(mcat_name)
                        ended_count += 1
                    else:
                        self.log(f"⚠️ Failed to end mining for {mcat_name}: {end_data.get('msg', 'Unknown error')}", Fore.YELLOW)
                except Exception as e:
                    self.log(f"⚠️ Exception ending mining for {mcat_name}: {e}", Fore.YELLOW)
            # Jika tidak semua cat berhasil di-ending, maka jangan lanjut ke deployment.
            if ended_count < len(mining_cats):
                self.log("⚠️ Not all mining cats could be ended. Skipping deployment.", Fore.YELLOW)
                return {"status": "success", "mining_summary": mining_summary}

            # === Step 5: Beli slot baru (jika memungkinkan, tapi lanjutkan jika gagal) ===
            self.log("📡 Attempting to buy a new mining slot...", Fore.CYAN)
            try:
                buy_slot_url = f"{self.BASE_URL}store/buySlot"
                buy_slot_response = requests.post(buy_slot_url, headers=headers)
                buy_slot_response.raise_for_status()
                buy_slot_data = buy_slot_response.json()
                if buy_slot_data.get("code") == 200:
                    self.log("✅ New mining slot bought successfully!", Fore.GREEN)
                else:
                    self.log(f"⚠️ Could not buy a new slot: {buy_slot_data.get('msg', 'Unknown error')}", Fore.YELLOW)
            except Exception as e:
                self.log(f"⚠️ Exception buying slot: {e}", Fore.YELLOW)

            # === Step 6: Ambil daftar cat milik user ===
            self.log("📡 Fetching user's cat list...", Fore.CYAN)
            try:
                user_cat_url = f"{self.BASE_URL}cat/user"
                user_response = requests.get(user_cat_url, headers=headers)
                user_response.raise_for_status()
                user_cat_data = user_response.json()
            except Exception as e:
                self.log(f"⚠️ Failed to fetch user's cat list: {e}", Fore.YELLOW)
                user_cat_data = {}
            if user_cat_data.get("code") == 200:
                cats = user_cat_data.get("result", {}).get("cats", [])
                self.log("✅ User's cat list retrieved successfully!", Fore.GREEN)
            else:
                self.log("⚠️ No valid user cat data.", Fore.YELLOW)
                cats = []

            # === Step 7: Urutkan cat berdasarkan profitabilitas (misal: mine_rate / time) ===
            def profit_metric(cat):
                t = cat.get("time", 0)
                return cat.get("mine_rate", 0) / t if t > 0 else 0
            cats.sort(key=profit_metric, reverse=True)
            self.log("📊 Cats sorted by profitability.", Fore.CYAN)

            # === Step 8: Deploy cat-cat hingga mine_capacity terpenuhi ===
            deployed_cats = []
            # Karena semua cat di-ending, maka slot yang tersedia sama dengan self.mine_capacity.
            available_slots = self.mine_capacity
            if available_slots <= 0:
                self.log("⚠️ No available mining slot for deployment.", Fore.YELLOW)
                return {"status": "success", "mining_summary": mining_summary}

            for cat in cats:
                if available_slots <= 0:
                    break
                cat_id = cat.get("cat_id")
                cat_name = cat.get("name", "Unknown")
                self.log(f"📡 Deploying {cat_name} to the mine...", Fore.CYAN)
                try:
                    deploy_url = f"{self.BASE_URL}mine/onCapacity?cat_id={cat_id}"
                    deploy_payload = {"cat_id": cat_id}
                    deploy_response = requests.post(deploy_url, headers=headers, json=deploy_payload)
                    deploy_response.raise_for_status()
                    deploy_data = deploy_response.json()
                    if deploy_data.get("code") == 200:
                        self.log(f"✅ {cat_name} deployed successfully!", Fore.GREEN)
                        deployed_cats.append(cat)
                        mining_summary["deployed"].append(cat_name)
                        available_slots -= 1
                    else:
                        self.log(f"⚠️ Failed to deploy {cat_name}: {deploy_data.get('msg', 'Unknown error')}", Fore.YELLOW)
                except Exception as e:
                    self.log(f"⚠️ Exception deploying {cat_name}: {e}", Fore.YELLOW)

            # === Step 9: Start mining untuk cat-cat yang telah di-deploy (jika belum 'working') ===
            for cat in deployed_cats:
                cat_id = cat.get("cat_id")
                cat_name = cat.get("name", "Unknown")
                if cat.get("stage", "").lower() != "working":
                    self.log(f"📡 Starting mining for {cat_name}...", Fore.CYAN)
                    try:
                        start_mining_url = f"{self.BASE_URL}mine/start?cat_id={cat_id}"
                        start_mining_payload = {"cat_id": cat_id}
                        start_mining_response = requests.post(start_mining_url, headers=headers, json=start_mining_payload)
                        start_mining_response.raise_for_status()
                        start_mining_data = start_mining_response.json()
                        if start_mining_data.get("code") == 200:
                            self.log(f"✅ {cat_name} started mining successfully!", Fore.GREEN)
                            mining_summary["started"].append(cat_name)
                        else:
                            self.log(f"⚠️ Failed to start mining for {cat_name}: {start_mining_data.get('msg', 'Unknown error')}", Fore.YELLOW)
                    except Exception as e:
                        self.log(f"⚠️ Exception starting mining for {cat_name}: {e}", Fore.YELLOW)

            # === Step 10: Klik SEMUA cat yang dideploy untuk bonus coin ===
            for cat in deployed_cats:
                cat_id = cat.get("cat_id")
                cat_name = cat.get("name", "Unknown")
                self.log(f"📡 Clicking cat {cat_id} for bonus coins...", Fore.CYAN)
                try:
                    click_url = f"{self.BASE_URL}mine/clickCat?cat_id={cat_id}&click_times=10"
                    click_response = requests.get(click_url, headers=headers)
                    click_response.raise_for_status()
                    click_data = click_response.json()
                    if click_data.get("code") == 200:
                        coins_earned = click_data.get("result", {}).get("coins", 0)
                        remaining_clicks = click_data.get("result", {}).get("remaining_clicks", 0)
                        self.log(f"✅ {cat_name} clicked successfully, earned {coins_earned} bonus coins! Remaining clicks: {remaining_clicks}", Fore.GREEN)
                        mining_summary["clicked"].append({
                            "cat": cat_name,
                            "coins_earned": coins_earned,
                            "remaining_clicks": remaining_clicks
                        })
                    else:
                        self.log(f"⚠️ Failed to click cat {cat_name}: {click_data.get('msg', 'Unknown error')}", Fore.YELLOW)
                except Exception as e:
                    self.log(f"⚠️ Exception clicking cat {cat_name}: {e}", Fore.YELLOW)

            return {"status": "success", "mining_summary": mining_summary}

        except requests.exceptions.RequestException as e:
            self.log(f"❌ Request failed: {e}", Fore.RED)
            return {"status": "error", "msg": f"Request failed: {e}"}
        except Exception as e:
            self.log(f"❌ An unexpected error occurred: {e}", Fore.RED)
            return {"status": "error", "msg": f"An unexpected error occurred: {e}"}
        
    def box(self):
        """
        Membuka semua lootbox yang tersedia.
        
        Selama self.claimed_lootboxes lebih dari 0, fungsi akan melakukan loop dan memanggil API
        {self.BASE_URL}lootbox/draw untuk membuka lootbox. Jika sukses, hasil (misalnya data cat)
        akan dikumpulkan dan self.claimed_lootboxes akan dikurangi satu setiap kali berhasil membuka.
        
        Returns:
            dict: Dictionary berisi status dan data lootbox yang berhasil dibuka.
        """
        try:
            self.update_info()
            headers = {"Authorization": self.token}
            opened_boxes = []  # Menyimpan data lootbox (misalnya cat) yang didapatkan

            # Loop selama masih ada lootbox yang belum diklaim
            while self.claimed_lootboxes > 0:
                self.log("📡 Drawing a lootbox...", Fore.CYAN)
                draw_url = f"{self.BASE_URL}lootbox/draw"
                response = requests.post(draw_url, headers=headers)
                response.raise_for_status()
                data = response.json()
                
                if data.get("code") == 200:
                    cat = data.get("result", {}).get("cat")
                    if cat:
                        cat_name = cat.get("name", "Unknown")
                        self.log(f"✅ Lootbox drawn successfully: obtained cat {cat_name}!", Fore.GREEN)
                        opened_boxes.append(cat)
                    else:
                        self.log("⚠️ Lootbox drawn but no cat found in result.", Fore.YELLOW)
                    # Kurangi jumlah lootbox yang belum diklaim
                    self.claimed_lootboxes -= 1
                else:
                    self.log(f"⚠️ Failed to draw lootbox: {data.get('msg', 'Unknown error')}", Fore.YELLOW)
                    break  # Hentikan loop jika terjadi error
            
            if opened_boxes:
                return {"status": "success", "opened_boxes": opened_boxes}
            else:
                self.log("❌ No lootboxes were drawn.", Fore.RED)
                return {"status": "error", "msg": "No lootboxes were drawn."}
        
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Request failed: {e}", Fore.RED)
            return {"status": "error", "msg": f"Request failed: {e}"}
        except Exception as e:
            self.log(f"❌ An unexpected error occurred: {e}", Fore.RED)
            return {"status": "error", "msg": f"An unexpected error occurred: {e}"}

if __name__ == "__main__":
    cat = memeCatMiner()
    index = 0
    max_index = len(cat.query_list)
    config = cat.load_config()

    cat.log("🎉 [LIVEXORDS] === Welcome to Meme Car Miner Automation === [LIVEXORDS]", Fore.YELLOW)
    cat.log(f"📂 Loaded {max_index} accounts from query list.", Fore.YELLOW)

    while True:
        current_account = cat.query_list[index]
        display_account = current_account[:10] + "..." if len(current_account) > 10 else current_account

        cat.log(f"👤 [ACCOUNT] Processing account {index + 1}/{max_index}: {display_account}", Fore.YELLOW)

        cat.login(index)

        cat.log("🛠️ Starting task execution...")
        tasks = [
            ("task", "🌞 Auto Complete Task"),
            ("box", "📦 Open Loot Box"),
            ("mining", "⛏️ Mining and Cat Deployment - First"),
            ("cat", "💳 Cat Purchase and Collection"),
            ("mining", "⛏️ Mining and Cat Deployment - Last")
        ]

        for task_key, task_name in tasks:
            task_status = config.get(task_key, False)
            cat.log(
                f"[CONFIG] {task_name}: {'✅ Enabled' if task_status else '❌ Disabled'}",
                Fore.YELLOW if task_status else Fore.RED,
            )

            if task_status:
                cat.log(f"🔄 Executing {task_name}...")
                getattr(cat, task_key)()

        if index == max_index - 1:
            cat.log("🔁 All accounts processed. Restarting loop.")
            cat.log(f"⏳ Sleeping for {config.get('delay_loop', 30)} seconds before restarting.")
            time.sleep(config.get("delay_loop", 30))
            index = 0
        else:
            cat.log(f"➡️ Switching to the next account in {config.get('delay_account_switch', 10)} seconds.")
            time.sleep(config.get("delay_account_switch", 10))
            index += 1
