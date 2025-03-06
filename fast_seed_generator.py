from mnemonic import Mnemonic
import multiprocessing
from multiprocessing import Pool
import sys
import time
from typing import List
import argparse
from colorama import Fore, init
from pyfiglet import Figlet

# Initialize colorama
init()

def print_banner():
    """Print a cool banner."""
    f = Figlet(font='slant')
    print(Fore.CYAN + f.renderText('Fast Seed Gen') + Fore.RESET)
    print(Fore.YELLOW + "Ultra Fast BIP39 Seed Generator" + Fore.RESET)
    print(Fore.RED + "=" * 50 + Fore.RESET + "\n")

def generate_seed(bits: int) -> str:
    """Generate a single seed phrase."""
    mnemo = Mnemonic("english")
    return mnemo.generate(strength=bits)

def worker_process(args):
    """Worker process for parallel generation."""
    bits, _ = args
    try:
        return generate_seed(bits)
    except Exception as e:
        print(f"Error in worker: {e}")
        return None

def save_seeds_batch(seeds: List[str], word_count: int):
    """Save a batch of generated seed phrases to a file."""
    filename = f"fast_seeds_{word_count}words.txt"
    
    with open(filename, 'a', buffering=8192) as f:
        for seed in seeds:
            f.write(f"{seed}\n")

def generate_continuously(word_count: int):
    """Generate seed phrases continuously using multiprocessing."""
    try:
        count = 0
        batch_size = 25000  # Larger batch size for better performance
        seed_batch = []
        bits = 128 if word_count == 12 else 256
        
        # Use all available CPU cores for maximum speed
        num_processes = multiprocessing.cpu_count()
        print(f"{Fore.YELLOW}Using {num_processes} processes for parallel generation{Fore.RESET}")
        
        start_time = time.time()
        last_update = start_time
        last_save_time = start_time
        
        with Pool(processes=num_processes) as pool:
            args_iter = ((bits, i) for i in range(sys.maxsize))
            
            for seed in pool.imap_unordered(worker_process, args_iter, chunksize=250):
                if seed:
                    count += 1
                    seed_batch.append(seed)
                    
                    # Update display every 0.5 seconds
                    current_time = time.time()
                    if current_time - last_update >= 0.5:
                        elapsed = current_time - start_time
                        speed = count / elapsed
                        total_saved = count - len(seed_batch)
                        print(f"\r{Fore.GREEN}Generated: {count:,} seeds | Speed: {speed:,.2f} seeds/sec | Saved: {total_saved:,}{Fore.RESET}", end='')
                        last_update = current_time
                    
                    # Save batch when it reaches batch_size or every 3 seconds
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
    parser = argparse.ArgumentParser(description='Ultra Fast BIP39 Seed Generator')
    parser.add_argument('--words', type=int, choices=[12, 24], default=12,
                      help='Number of words in the seed phrase (12 or 24)')
    
    args = parser.parse_args()
    
    try:
        print_banner()
        print(f"{Fore.YELLOW}Starting ultra-fast generation mode...")
        print(f"{Fore.RED}Press Ctrl+C to stop{Fore.RESET}")
        generate_continuously(args.words)
        
    except Exception as e:
        print(f"{Fore.RED}Error: {str(e)}{Fore.RESET}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main() 