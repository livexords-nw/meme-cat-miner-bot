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

    def banner(self) -> None:
        """Displays the banner for the bot."""
        self.log("🎉 Meme Cat Mainer Free Bot", Fore.CYAN)
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

        self.log(
            f"📋 Using payload: telegram_id={telegram_id}, user_name={user_name}",
            Fore.CYAN,
        )

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

                reward = result.get("reward", {})
                coins = reward.get("coins", 0)
                claimed_lootboxes = reward.get("claimed_lootboxes", 0)
                new_player = result.get("new_player", False)

                self.log(f"💰 Coins: {coins}", Fore.CYAN)
                self.log(f"📦 Claimed Lootboxes: {claimed_lootboxes}", Fore.LIGHTYELLOW_EX)
                self.log(f"🆕 New Player: {new_player}", Fore.LIGHTBLUE_EX)
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
            coins = result.get("coins", 0)
            name = result.get("name", "Unknown")
            self.level = result.get("level", 0)
            rank = result.get("level_info", {}).get("rank", "Unknown")
            avatar = result.get("avatar", "")

            self.log("✅ Player info updated successfully!", Fore.GREEN)
            self.log(f"👤 Name: {name}", Fore.LIGHTGREEN_EX)
            self.log(f"💎 Coins: {coins}", Fore.CYAN)
            self.log(f"🎖️ Level: {self.level} ({rank})", Fore.LIGHTBLUE_EX)
            self.log(f"🖼️ Avatar: {avatar}", Fore.LIGHTMAGENTA_EX)

            return {
                "name": name,
                "coins": coins,
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
        Handles task-related operations, including listing tasks, completing tasks, and performing daily check-in.

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

        except requests.exceptions.RequestException as e:
            self.log(f"❌ Task operation failed: {e}", Fore.RED)
            return summary
        except Exception as e:
            self.log(f"❌ An unexpected error occurred: {e}", Fore.RED)
            return summary

        return summary

    def cat(self):
        """
        Fetches the cat list and attempts to purchase the most expensive cat available for the user's level 
        until no more cats can be bought.

        Returns:
            dict: A dictionary containing the result of the operation.
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

            # Step 2: Update user info (including coins and level)
            self.update_info()

            available_cats = [cat for cat in cats if cat['level_limit'] <= self.level]
            
            available_cats.sort(key=lambda cat: cat['price'], reverse=True)

            purchased_cats = []

            # Step 3: Try to purchase the most expensive cat that can be bought
            for cat in available_cats:
                if self.coins >= cat['price']:
                    self.log(f"📡 Attempting to buy {cat['name']} for {cat['price']} coins...", Fore.CYAN)
                    buy_cat_url = f"{self.BASE_URL}store/buyCat"
                    payload = {"breed_id": cat['breed_id']}
                    response = requests.post(buy_cat_url, headers=headers, json=payload)
                    response.raise_for_status()

                    buy_data = response.json()
                    if buy_data.get("code") == 200:
                        self.log(f"✅ Successfully purchased {cat['name']}!", Fore.GREEN)
                        purchased_cats.append(cat['name'])
                        break  
                    else:
                        self.log(f"⚠️ Failed to purchase {cat['name']}: {buy_data.get('msg', 'Unknown error')}", Fore.YELLOW)
                else:
                    self.log(f"⚠️ Not enough coins to buy {cat['name']}. Searching for another cat...", Fore.YELLOW)
            
            if purchased_cats:
                return {"status": "success", "purchased_cats": purchased_cats}
            else:
                self.log("❌ No cats could be purchased.", Fore.RED)
                return {"status": "error", "msg": "No cats could be purchased."}

        except requests.exceptions.RequestException as e:
            self.log(f"❌ Request failed: {e}", Fore.RED)
            return {"status": "error", "msg": f"Request failed: {e}"}
        except Exception as e:
            self.log(f"❌ An unexpected error occurred: {e}", Fore.RED)
            return {"status": "error", "msg": f"An unexpected error occurred: {e}"}

    def mining(self):
        """
        Handles mining-related operations for available cats.

        Checks the user's cat list, deploys the cat to the field if it's not already there,
        starts the mining process for eligible cats, clicks the cat for coins, and buys additional slots if needed.

        Returns:
            dict: A dictionary summarizing the mining status and any errors encountered.
        """
        try:
            headers = {"Authorization": self.token}

            # Step 1: Fetch cat list
            self.log("📡 Fetching cat list...", Fore.CYAN)
            cat_list_url = f"{self.BASE_URL}cat/list"
            response = requests.get(cat_list_url, headers=headers)
            response.raise_for_status()

            cat_data = response.json()
            if cat_data.get("code") != 200:
                self.log(f"⚠️ Failed to fetch cat list: {cat_data.get('msg', 'Unknown error')}", Fore.YELLOW)
                return {"status": "error", "msg": "Failed to fetch cat list"}

            cats = cat_data.get("result", {}).get("cats", [])
            self.log("✅ Cat list retrieved successfully!", Fore.GREEN)

            # Step 2: Deploy and start mining for eligible cats
            mining_summary = {"deployed_cats": [], "mining_started": [], "clicked_cats": []}

            for cat in cats:
                if cat['user_owned'] == 1:
                    cat_id = cat['user_cat_info'][0]['cat_id']
                    if cat['user_mining'] == 0:
                        if self.check_available_slots() == 0:
                            self.log(f"⚠️ No available slots for {cat['name']}, attempting to buy a slot...", Fore.YELLOW)
                            buy_slot_url = f"{self.BASE_URL}store/buySlot"
                            buy_slot_response = requests.post(buy_slot_url, headers=headers)
                            buy_slot_response.raise_for_status()

                            buy_slot_data = buy_slot_response.json()
                            if buy_slot_data.get("code") == 400 and "Coins not enough" in buy_slot_data.get("msg", ""):
                                self.log("⚠️ Not enough coins to buy an additional slot.", Fore.YELLOW)
                                return {"status": "error", "msg": "Not enough coins to buy additional slot."}
                            else:
                                self.log("✅ Slot bought successfully!", Fore.GREEN)

                        self.log(f"📡 Deploying {cat['name']} to the field...", Fore.CYAN)
                        deploy_url = f"{self.BASE_URL}mine/onCapacity?cat_id={cat_id}"
                        deploy_payload = {"cat_id": cat_id}
                        deploy_response = requests.post(deploy_url, headers=headers, json=deploy_payload)
                        deploy_response.raise_for_status()

                        deploy_data = deploy_response.json()
                        if deploy_data.get("code") == 400 and "already in field" in deploy_data.get("msg", "").lower():
                            self.log(f"⚠️ {cat['name']} is already in the field.", Fore.YELLOW)
                        else:
                            self.log(f"✅ {cat['name']} deployed successfully!", Fore.GREEN)
                            mining_summary["deployed_cats"].append(cat['name'])

                        # Step 3: Start mining for the cat if it's not already mining
                        self.log(f"📡 Starting mining for {cat['name']}...", Fore.CYAN)
                        start_mining_url = f"{self.BASE_URL}mine/start?cat_id={cat_id}"
                        start_mining_payload = {"cat_id": cat_id}
                        start_mining_response = requests.post(start_mining_url, headers=headers, json=start_mining_payload)
                        start_mining_response.raise_for_status()

                        start_mining_data = start_mining_response.json()
                        if start_mining_data.get("code") == 400 and "already mining" in start_mining_data.get("msg", "").lower():
                            self.log(f"⚠️ {cat['name']} is already mining.", Fore.YELLOW)
                        else:
                            self.log(f"✅ {cat['name']} started mining successfully!", Fore.GREEN)
                            mining_summary["mining_started"].append(cat['name'])

                    # Step 4: Click the cat to get coins (10 times)
                    if cat['user_mining'] == 1:
                        self.log(f"📡 Clicking {cat['name']} to collect coins...", Fore.CYAN)
                        click_url = f"{self.BASE_URL}mine/clickCat?cat_id={cat_id}&click_times=10"
                        click_response = requests.get(click_url, headers=headers)
                        click_response.raise_for_status()

                        click_data = click_response.json()
                        if click_data.get("code") == 200:
                            coins_earned = click_data.get("result", {}).get("coins", 0)
                            self.log(f"✅ {cat['name']} clicked successfully, earned {coins_earned} coins!", Fore.GREEN)
                            mining_summary["clicked_cats"].append(cat['name'])

                if not mining_summary["deployed_cats"] and not mining_summary["mining_started"] and not mining_summary["clicked_cats"]:
                    self.log("❌ No cats were deployed, mining started, or clicked.", Fore.RED)
                    return {"status": "error", "msg": "No cats were deployed, mining started, or clicked."}

                return {"status": "success", "mining_summary": mining_summary}

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
        tasks = {
            "task": "🌞 Auto Complete Task",  
            "cat": "💳 Cat Purchase and Collection", 
            "mining": "⛏️ Mining and Cat Deployment", 
        }


        for task_key, task_name in tasks.items():
            task_status = config.get(task_key, False)
            cat.log(f"[CONFIG] {task_name}: {'✅ Enabled' if task_status else '❌ Disabled'}", Fore.YELLOW if task_status else Fore.RED)

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