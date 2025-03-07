from mnemonic import Mnemonic
import argparse
import sys
from typing import List, Optional
import json
from colorama import Fore, init
from hdwallet.symbols import BTC, ETH
from hdwallet import HDWallet
import requests
from pyfiglet import Figlet
import time
import multiprocessing
from multiprocessing import Pool, Manager
import os

# Initialize colorama
init()

def print_banner():
    """Print a cool banner."""
    f = Figlet(font='slant')
    print(Fore.CYAN + f.renderText('Seed Gen') + Fore.RESET)
    print(Fore.YELLOW + "BIP39 Seed Phrase Generator" + Fore.RESET)
    print(Fore.RED + "=" * 50 + Fore.RESET + "\n")

def get_all_bip39_words() -> List[str]:
    """Get all 2048 BIP39 words."""
    mnemo = Mnemonic("english")
    return mnemo.wordlist

def save_wordlist_to_file(filename: str = "bip39_wordlist.txt"):
    """Save all 2048 BIP39 words to a file."""
    words = get_all_bip39_words()
    
    # Save as plain text
    with open(filename, 'w') as f:
        for i, word in enumerate(words, 1):
            f.write(f"{i:4d}. {word}\n")
    
    # Save as JSON for programmatic access
    with open('bip39_wordlist.json', 'w') as f:
        json.dump({"words": words}, f, indent=2)
    
    print(f"\nWordlist saved to {filename} and bip39_wordlist.json")

def generate_seed_phrase(word_count=12) -> str:
    """Generate a BIP39 seed phrase with specified number of words."""
    if word_count not in [12, 24]:
        raise ValueError("Word count must be either 12 or 24")
    
    # Create a mnemonic code object (English wordlist)
    mnemo = Mnemonic("english")
    
    # Generate words based on the specified length
    # 128 bits for 12 words, 256 bits for 24 words
    bits = 128 if word_count == 12 else 256
    words = mnemo.generate(strength=bits)
    
    return words

def generate_addresses(seed_phrase: str) -> tuple:
    """Generate BTC and ETH addresses from seed phrase."""
    try:
        # Initialize HDWallet for BTC
        btc_wallet = HDWallet(symbol=BTC)
        btc_wallet.from_mnemonic(seed_phrase)
        btc_wallet.from_path("m/44'/0'/0'/0/0")
        btc_address = btc_wallet.p2pkh_address()
        
        # Initialize HDWallet for ETH
        eth_wallet = HDWallet(symbol=ETH)
        eth_wallet.from_mnemonic(seed_phrase)
        eth_wallet.from_path("m/44'/60'/0'/0/0")
        eth_address = eth_wallet.p2pkh_address()
        
        return btc_address, eth_address
    except Exception as e:
        print(f"{Fore.RED}Error generating addresses: {str(e)}{Fore.RESET}")
        return None, None

def check_balance(btc_address: str, eth_address: str) -> tuple:
    """Check BTC and ETH balances."""
    try:
        # Check BTC balance
        btc_response = requests.get(f"https://blockchain.info/balance?active={btc_address}")
        btc_balance = btc_response.json()[btc_address]['final_balance'] / 100000000
        
        # Check ETH balance
        eth_response = requests.get(f"https://api.etherscan.io/api?module=account&action=balance&address={eth_address}&tag=latest")
        eth_balance = int(eth_response.json()['result']) / 1000000000000000000
        
        return btc_balance, eth_balance
    except:
        return 0, 0

def generate_single_wallet(bits: int) -> tuple:
    """Generate a single wallet with addresses."""
    mnemo = Mnemonic("english")
    words = mnemo.generate(strength=bits)
    
    # Generate addresses
    btc_wallet = HDWallet(symbol=BTC)
    btc_wallet.from_mnemonic(words)
    btc_wallet.from_path("m/44'/0'/0'/0/0")
    btc_address = btc_wallet.p2pkh_address()
    
    eth_wallet = HDWallet(symbol=ETH)
    eth_wallet.from_mnemonic(words)
    eth_wallet.from_path("m/44'/60'/0'/0/0")
    eth_address = eth_wallet.p2pkh_address()
    
    return words, btc_address, eth_address

def worker_process(args):
    """Worker process for parallel generation."""
    bits, counter = args
    try:
        return generate_single_wallet(bits)
    except Exception as e:
        print(f"Error in worker: {e}")
        return None

def save_seed_phrases_batch(seed_data_batch: List[tuple], word_count: int):
    """Save a batch of generated seed phrases to a file."""
    filename = f"seed_phrases_{word_count}words.txt"
    
    with open(filename, 'a', buffering=8192) as f:  # Added buffering for better I/O performance
        for seed_phrase, _, _ in seed_data_batch:  # We only save the seed phrase
            f.write(f"{seed_phrase}\n")

def generate_continuously(word_count: int, no_save: bool = False, no_balance: bool = False):
    """Generate seed phrases continuously using multiprocessing."""
    try:
        count = 0
        batch_size = 10000  # Increased batch size since we're saving less data
        seed_data_batch = []
        bits = 128 if word_count == 12 else 256
        
        # Use number of CPU cores minus 1 to avoid system slowdown
        num_processes = max(1, multiprocessing.cpu_count() - 1)
        print(f"{Fore.YELLOW}Using {num_processes} processes for parallel generation{Fore.RESET}")
        
        start_time = time.time()
        last_update = start_time
        last_save_time = start_time
        
        with Pool(processes=num_processes) as pool:
            # Generate args for workers
            args_iter = ((bits, i) for i in range(sys.maxsize))
            
            # Process wallets in parallel
            for result in pool.imap_unordered(worker_process, args_iter, chunksize=100):
                if result:
                    words, btc_address, eth_address = result
                    count += 1
                    
                    # Calculate speed every second
                    current_time = time.time()
                    if current_time - last_update >= 1.0:
                        elapsed = current_time - start_time
                        speed = count / elapsed
                        total_saved = count - len(seed_data_batch)
                        print(f"\r{Fore.GREEN}Generated: {count} seed phrases | Speed: {speed:.2f} phrases/sec | Saved: {total_saved}{Fore.RESET}", end='')
                        last_update = current_time
                    
                    if not no_save:
                        seed_data_batch.append((words, btc_address, eth_address))
                        
                        # Save batch when it reaches batch_size or every 5 seconds
                        if len(seed_data_batch) >= batch_size or (current_time - last_save_time >= 5.0 and seed_data_batch):
                            save_seed_phrases_batch(seed_data_batch, word_count)
                            seed_data_batch = []
                            last_save_time = current_time
                            print(f"\n{Fore.YELLOW}Saved batch of seeds{Fore.RESET}")
                            
    except KeyboardInterrupt:
        print("\nStopping generation gracefully...")
        if seed_data_batch and not no_save:
            save_seed_phrases_batch(seed_data_batch, word_count)
        print(f"\n{Fore.RED}Generation stopped by user. Total generated: {count}{Fore.RESET}")
        sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description='Generate a BIP39 seed phrase')
    parser.add_argument('--words', type=int, choices=[12, 24], default=12,
                      help='Number of words in the seed phrase (12 or 24)')
    parser.add_argument('--show-wordlist', action='store_true',
                      help='Display all 2048 BIP39 words')
    parser.add_argument('--save-wordlist', action='store_true',
                      help='Save all 2048 BIP39 words to files')
    parser.add_argument('--no-save', action='store_true',
                      help='Do not save the generated seed phrases to files')
    parser.add_argument('--no-balance', action='store_true',
                      help='Do not check balances (faster generation)')
    parser.add_argument('--continuous', action='store_true',
                      help='Generate seed phrases continuously')
    
    args = parser.parse_args()
    
    try:
        print_banner()

        if args.save_wordlist:
            save_wordlist_to_file()
            return

        if args.show_wordlist:
            words = get_all_bip39_words()
            print("\nComplete list of 2048 BIP39 words:")
            print("=" * 50)
            for i, word in enumerate(words, 1):
                print(f"{i:4d}. {word}")
            print("=" * 50)
            return

        if args.continuous:
            print(f"\n{Fore.YELLOW}Starting continuous generation mode...")
            print(f"{Fore.RED}Press Ctrl+C to stop{Fore.RESET}")
            generate_continuously(args.words, args.no_save, args.no_balance)
            return

        seed_phrase = generate_seed_phrase(args.words)
        btc_address, eth_address = generate_addresses(seed_phrase)
        
        if btc_address and eth_address:
            if not args.no_balance:
                btc_balance, eth_balance = check_balance(btc_address, eth_address)
            
            print(f"\n{Fore.GREEN}Generated Seed Phrase:")
            print(Fore.WHITE + "=" * 50)
            print(seed_phrase)
            print("=" * 50)
            
            print(f"\n{Fore.YELLOW}Addresses:")
            print(f"BTC: {Fore.WHITE}{btc_address}")
            print(f"{Fore.YELLOW}ETH: {Fore.WHITE}{eth_address}")
            
            if not args.no_balance:
                print(f"\n{Fore.CYAN}Balances:")
                print(f"BTC: {Fore.WHITE}{btc_balance}")
                print(f"{Fore.CYAN}ETH: {Fore.WHITE}{eth_balance}")
            
            if not args.no_save:
                save_seed_phrases_batch([(seed_phrase, btc_address, eth_address)], args.words)
            
            print(f"\n{Fore.RED}WARNING: Store this seed phrase securely! Never share it with anyone!")
            print(f"Anyone with access to this phrase can access your crypto assets.{Fore.RESET}\n")
    
    except Exception as e:
        print(f"{Fore.RED}Error: {str(e)}{Fore.RESET}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main() 