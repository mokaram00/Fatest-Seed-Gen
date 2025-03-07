from mnemonic import Mnemonic
import multiprocessing
from multiprocessing import Pool
import sys
import time
from typing import List, Optional
import argparse
from colorama import Fore, init
from pyfiglet import Figlet
from hdwallet import HDWallet
from hdwallet.symbols import *
from hdwallet.derivations import BIP44Derivation
from hdwallet.utils import generate_mnemonic
from bip_utils import Bip39MnemonicGenerator, Bip44, Bip44Coins, Bip44Changes, Bip44Levels
from bip_utils import Bip39SeedGenerator, Bip44
from typing import Dict, Any
import itertools

# Initialize colorama
init()

# Supported Standards
SUPPORTED_STANDARDS = {
    "BIP39": "BIP39 Standard",
    "BIP44": "BIP44 Path Standard",
    "SLIP39": "SLIP39 Shared Wallet Standard",
    "MONERO": "Monero Standard",
    "SOLANA": "Solana Standard"
}

# Supported Networks with their paths and coin types
SUPPORTED_NETWORKS = {
    # HDWallet Networks - Only include networks that are actually available
    "BTC": {"name": "Bitcoin", "path": "m/44'/0'/0'/0/0", "type": "hdwallet"},
    "ETH": {"name": "Ethereum", "path": "m/44'/60'/0'/0/0", "type": "hdwallet"},
    "BCH": {"name": "Bitcoin Cash", "path": "m/44'/145'/0'/0/0", "type": "hdwallet"},
    "LTC": {"name": "Litecoin", "path": "m/44'/2'/0'/0/0", "type": "hdwallet"},
    "DASH": {"name": "Dash", "path": "m/44'/5'/0'/0/0", "type": "hdwallet"},
    "DOGE": {"name": "Dogecoin", "path": "m/44'/3'/0'/0/0", "type": "hdwallet"},
    "ZEC": {"name": "Zcash", "path": "m/44'/133'/0'/0/0", "type": "hdwallet"},
    "RVN": {"name": "Ravencoin", "path": "m/44'/175'/0'/0/0", "type": "hdwallet"},
    "QTUM": {"name": "Qtum", "path": "m/44'/88'/0'/0/0", "type": "hdwallet"},
    "ZEN": {"name": "Horizen", "path": "m/44'/121'/0'/0/0", "type": "hdwallet"},
    "TRX": {"name": "TRON", "path": "m/44'/195'/0'/0/0", "type": "hdwallet"},
    "ATOM": {"name": "Cosmos", "path": "m/44'/118'/0'/0/0", "type": "hdwallet"},
    # BIP Utils Networks
    "SOL": {"name": "Solana", "path": "m/44'/501'/0'/0/0", "type": "bip_utils", "coin_type": Bip44Coins.SOLANA},
    "MATIC": {"name": "Polygon", "path": "m/44'/966'/0'/0/0", "type": "bip_utils", "coin_type": Bip44Coins.POLYGON},
    "AVAX": {"name": "Avalanche", "path": "m/44'/9000'/0'/0/0", "type": "bip_utils", "coin_type": Bip44Coins.AVAX_C_CHAIN},
    "DOT": {"name": "Polkadot", "path": "m/44'/354'/0'/0/0", "type": "bip_utils", "coin_type": Bip44Coins.POLKADOT_ED25519_SLIP},
    "XRP": {"name": "Ripple", "path": "m/44'/144'/0'/0/0", "type": "bip_utils", "coin_type": Bip44Coins.RIPPLE}
}

def print_banner():
    """Print a cool banner."""
    f = Figlet(font='slant')
    print(Fore.CYAN + f.renderText('Fast Seed Gen') + Fore.RESET)
    print(Fore.YELLOW + "Multi-Standard Wallet Seed Generator" + Fore.RESET)
    print(Fore.RED + "=" * 50 + Fore.RESET + "\n")

def generate_seed(bits: int, standard: str = "BIP39", network: str = "BTC") -> Dict[str, Any]:
    """Generate a seed phrase based on the specified standard."""
    try:
        if standard == "BIP39":
            mnemo = Mnemonic("english")
            seed = mnemo.generate(strength=bits)
            return {"seed": seed, "standard": standard}
            
        elif standard == "BIP44":
            network_info = SUPPORTED_NETWORKS[network]
            
            if network_info["type"] == "hdwallet":
                # Generate BIP44 seeds with different network support using hdwallet
                hdwallet = HDWallet(symbol=network)
                hdwallet.from_mnemonic(generate_mnemonic(language="english", strength=bits))
                hdwallet.from_path(network_info["path"])
                return {
                    "seed": hdwallet.mnemonic(),
                    "address": hdwallet.p2pkh_address(),
                    "standard": standard,
                    "network": network,
                    "network_name": network_info["name"]
                }
            else:
                try:
                    # Generate BIP44 seeds using bip_utils
                    words = 12 if bits == 128 else 24
                    mnemonic = Bip39MnemonicGenerator().FromWordsNumber(words)
                    # Generate seed from mnemonic
                    seed_bytes = Bip39SeedGenerator(mnemonic).Generate()
                    # Create BIP44 wallet with specific coin type
                    bip44_wallet = Bip44.FromSeed(seed_bytes, network_info["coin_type"])
                    
                    return {
                        "seed": str(mnemonic),
                        "standard": standard,
                        "network": network,
                        "network_name": network_info["name"]
                    }
                except Exception as e:
                    print(f"Error with {network}: {str(e)}")
                    # Fallback to BIP39 if coin type not supported
                    mnemo = Mnemonic("english")
                    seed = mnemo.generate(strength=bits)
                    return {"seed": seed, "standard": "BIP39", "network": network}
            
        elif standard == "SLIP39":
            # Generate SLIP39 seeds (shared wallets)
            mnemo = Mnemonic("english")
            seed = mnemo.generate(strength=bits)
            return {"seed": seed, "standard": standard}
            
        elif standard == "MONERO":
            # Generate Monero seeds
            mnemo = Mnemonic("english")
            seed = mnemo.generate(strength=bits)
            return {"seed": seed, "standard": standard}
            
        elif standard == "SOLANA":
            # Generate Solana seeds
            mnemo = Mnemonic("english")
            seed = mnemo.generate(strength=bits)
            return {"seed": seed, "standard": standard}
            
        else:
            raise ValueError(f"Unsupported standard: {standard}")
            
    except Exception as e:
        print(f"Error generating seed: {e}")
        return None

def worker_process(args):
    """Worker process for parallel generation."""
    bits, standard, network = args
    try:
        return generate_seed(bits, standard, network)
    except Exception as e:
        print(f"Error in worker: {e}")
        return None

def save_seeds_batch(seeds: List[Dict[str, Any]], word_count: int):
    """Save a batch of generated seed phrases to a file."""
    filename = f"fast_seeds_{word_count}words.txt"
    
    with open(filename, 'a', buffering=8192) as f:
        for seed_data in seeds:
            if seed_data:
                f.write(f"{seed_data['seed']}\n")

def generate_continuously(word_count: int):
    """Generate seed phrases continuously using multiprocessing for all standards."""
    try:
        count = 0
        batch_size = 100000
        seed_batch = []
        bits = 128 if word_count == 12 else 256
        
        num_processes = multiprocessing.cpu_count()
        print(f"{Fore.YELLOW}Using {num_processes} processes for parallel generation{Fore.RESET}")
        
        start_time = time.time()
        last_update = start_time
        last_save_time = start_time
        
        # Create list of all possible combinations of standards and networks
        combinations = []
        for standard in SUPPORTED_STANDARDS.keys():
            if standard == "BIP44":
                # Add BIP44 with each network
                for network in SUPPORTED_NETWORKS.keys():
                    combinations.append((bits, standard, network))
            else:
                # Add other standards without network
                combinations.append((bits, standard, "BTC"))
        
        with Pool(processes=num_processes) as pool:
            args_iter = itertools.cycle(combinations)
            
            for seed_data in pool.imap_unordered(worker_process, args_iter, chunksize=1000):
                if seed_data:
                    count += 1
                    seed_batch.append(seed_data)
                    
                    current_time = time.time()
                    if current_time - last_update >= 0.5:
                        elapsed = current_time - start_time
                        speed = count / elapsed
                        total_saved = count - len(seed_batch)
                        print(f"\r{Fore.GREEN}Generated: {count:,} seeds | Speed: {speed:,.2f} seeds/sec | Saved: {total_saved:,}{Fore.RESET}", end='')
                        last_update = current_time
                    
                    if len(seed_batch) >= batch_size or (current_time - last_save_time >= 3.0 and seed_batch):
                        save_seeds_batch(seed_batch, word_count)
                        seed_batch = []
                        last_save_time = current_time
                        print(f"\n{Fore.YELLOW}Saved batch of seeds{Fore.RESET}")
                            
    except KeyboardInterrupt:
        print("\nStopping generation gracefully...")
        if seed_batch:
            save_seeds_batch(seed_batch, word_count)
        print(f"\n{Fore.RED}Generation stopped by user. Total generated: {count:,}{Fore.RESET}")
        sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description='Multi-Standard Wallet Seed Generator')
    parser.add_argument('--words', type=int, choices=[12, 24], default=12,
                      help='Number of words in the seed phrase (12 or 24)')
    
    args = parser.parse_args()
    
    try:
        print_banner()
        print(f"{Fore.YELLOW}Starting fast generation mode for all standards...")
        print(f"{Fore.RED}Press Ctrl+C to stop{Fore.RESET}")
        print(f"{Fore.CYAN}Generating seeds for all supported standards:{Fore.RESET}")
        for standard, desc in SUPPORTED_STANDARDS.items():
            print(f"- {desc}")
        print(f"\n{Fore.CYAN}Supported networks ({len(SUPPORTED_NETWORKS)}):{Fore.RESET}")
        for network, info in SUPPORTED_NETWORKS.items():
            print(f"- {info['name']} ({network})")
        generate_continuously(args.words)
        
    except Exception as e:
        print(f"{Fore.RED}Error: {str(e)}{Fore.RESET}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main() 