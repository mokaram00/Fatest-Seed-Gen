# 🔐 Crypto Wallet & Seed Generators

A powerful Python toolkit featuring two specialized generators:
1. Full-featured cryptocurrency wallet generator
2. Ultra-fast seed phrase generator

## ✨ Features

### Seed Phrase Generation
- Two specialized generators for different needs:
  - `seed_generator.py`: Full wallet generation with addresses
  - `fast_seed_generator.py`: Ultra-fast seed phrase generation only
- Generate 12 or 24-word seed phrases
- Uses cryptographically secure random number generation
- Follows BIP39 standard for maximum compatibility
- Support for multiple languages (currently English)
- Parallel processing for maximum performance

### Wallet Features (seed_generator.py)
- Automatically generates BTC (Bitcoin) addresses
- Automatically generates ETH (Ethereum) addresses
- Optional real-time balance checking for both BTC and ETH
- Supports standard derivation paths (m/44'/0'/0'/0/0 for BTC, m/44'/60'/0'/0/0 for ETH)

### User Interface
- Beautiful colored command-line interface
- Clear and organized output format
- Real-time progress indicators and speed metrics
- Easy-to-use command-line arguments
- Performance statistics display

### Data Management
- Automatic saving of generated seed phrases
- Configurable batch sizes for optimal performance
- Option to view all 2048 BIP39 words
- Save word list in both TXT and JSON formats
- Continuous generation mode with auto-save
- Buffered file writing for better performance

### Performance Features (fast_seed_generator.py)
- Multi-core processing utilizing all CPU cores
- Optimized for maximum seed generation speed
- Large batch processing (25,000 seeds per batch)
- Minimal disk I/O with buffered writing
- Real-time speed metrics (seeds/second)
- Memory-efficient operation

### Security Features
- No online storage of seed phrases
- Local file storage only
- Clear security warnings and guidelines
- Error handling and validation
- Graceful shutdown with data preservation

## 🚀 Installation

1. Make sure you have Python 3.7+ installed
2. Clone this repository
3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## 💻 Usage

### Full Wallet Generator (seed_generator.py)

Generate a single 12-word seed phrase with addresses:
```bash
python seed_generator.py
```

Continuous generation with addresses:
```bash
python seed_generator.py --continuous
```

Fast generation (without balance checking):
```bash
python seed_generator.py --continuous --no-balance
```

Additional options:
```bash
python seed_generator.py --words 24  # Generate 24-word phrases
python seed_generator.py --show-wordlist  # Show all BIP39 words
python seed_generator.py --save-wordlist  # Save wordlist to file
python seed_generator.py --no-save  # Generate without saving
```

### Ultra-Fast Generator (fast_seed_generator.py)

Generate seeds at maximum speed:
```bash
python fast_seed_generator.py
```

Generate 24-word seeds at maximum speed:
```bash
python fast_seed_generator.py --words 24
```

### Speed Comparison
- `seed_generator.py --continuous --no-balance`: Generates seeds with addresses
- `fast_seed_generator.py`: Maximum speed seed-only generation (multiple times faster)

## 📋 Output Format

### seed_generator.py
- Seed Phrase
- BTC Address
- ETH Address
- Current BTC Balance (optional)
- Current ETH Balance (optional)

### fast_seed_generator.py
- Seed Phrases only
- Real-time generation speed
- Total seeds generated
- Batch save status

## ⚠️ Security Warnings

- Never share your seed phrases with anyone
- Store seed phrases securely offline
- This tool is for educational purposes only
- Always verify cryptocurrency addresses before sending funds
- Keep your seed phrases private and secure
- No responsibility is taken for lost or stolen funds

## 🔍 Technical Details

- Uses BIP39 standard for seed phrase generation
- Implements BIP32/44 for HD wallet derivation (in seed_generator.py)
- Real-time balance checking via blockchain APIs (optional in seed_generator.py)
- Supports multiple address formats
- Follows cryptocurrency best practices
- Optimized parallel processing
- Efficient memory and disk usage

## 📝 License

This project is for educational purposes only. Use at your own risk.

## 🤝 Contributing & Development

### Setting up Development Environment

1. Fork the repository
2. Clone your fork:
```bash
git clone https://github.com/YOUR_USERNAME/cryptowallets-seedgen.git
cd cryptowallets-seedgen
```

3. Create a new branch:
```bash
git checkout -b feature/your-feature-name
```

4. Make your changes and test them
5. Commit your changes:
```bash
git add .
git commit -m "Add: your feature description"
```

6. Push to your fork:
```bash
git push origin feature/your-feature-name
```

7. Create a Pull Request from your fork to our main repository

### Code Style
- Follow PEP 8 guidelines
- Add comments for complex logic
- Update documentation for new features
- Include appropriate error handling

Feel free to submit issues and enhancement requests. All contributions are welcome! 