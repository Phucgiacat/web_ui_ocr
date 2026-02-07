"""
Proxy Manager - Quản lý rotation proxy với error handling
"""

import random
import os
from pathlib import Path
from typing import List, Optional
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm


class ProxyManager:
    """
    Quản lý danh sách proxy và rotation tự động
    
    Features:
    - Load proxy từ file http.txt
    - Random selection
    - Auto remove failed proxies
    - Thread-safe operations
    """
    
    def __init__(self, proxy_file: str = None, use_validated: bool = True):
        """
        Args:
            proxy_file: Đường dẫn đến file chứa danh sách proxy
            use_validated: Nếu True, load từ file validated (nếu có)
        """
        if proxy_file is None:
            # Default: http.txt ở thư mục root
            proxy_file = Path(__file__).parent.parent / "http.txt"
        
        self.proxy_file = proxy_file
        self.validated_file = Path(self.proxy_file).parent / "http_validated.txt"
        self.proxies: List[str] = []
        self.failed_proxies: List[str] = []
        self.use_validated = use_validated
        self.load_proxies()
    
    def load_proxies(self):
        """Load danh sách proxy từ file (ưu tiên file validated)"""
        # Nếu có file validated và use_validated=True, load từ đó
        if self.use_validated and os.path.exists(self.validated_file):
            with open(self.validated_file, 'r', encoding='utf-8') as f:
                self.proxies = [line.strip() for line in f if line.strip()]
            print(f"✅ Loaded {len(self.proxies)} VALIDATED proxies from {self.validated_file.name}")
            return
        
        # Không thì load từ file gốc
        if not os.path.exists(self.proxy_file):
            raise FileNotFoundError(f"Proxy file not found: {self.proxy_file}")
        
        with open(self.proxy_file, 'r', encoding='utf-8') as f:
            self.proxies = [line.strip() for line in f if line.strip()]
        
        print(f"✅ Loaded {len(self.proxies)} proxies from {self.proxy_file}")
        print(f"⚠️ Consider running validate_proxies() to filter working proxies")
    
    def get_random_proxy(self) -> Optional[dict]:
        """
        Lấy 1 proxy ngẫu nhiên từ danh sách còn lại
        
        Returns:
            dict: {'http': 'http://ip:port', 'https': 'http://ip:port'} hoặc None
        """
        if not self.proxies:
            print("⚠️ No proxies available!")
            return None
        
        proxy = random.choice(self.proxies)
        
        # Format: {'http': 'http://ip:port', 'https': 'http://ip:port'}
        return {
            'http': f'http://{proxy}',
            'https': f'http://{proxy}'
        }
    
    def mark_failed(self, proxy_dict: dict):
        """
        Đánh dấu proxy thất bại và loại bỏ khỏi danh sách
        
        Args:
            proxy_dict: Dict chứa proxy info
        """
        if not proxy_dict:
            return
        
        # Extract IP:PORT từ dict
        proxy_str = proxy_dict.get('http', '').replace('http://', '')
        
        if proxy_str in self.proxies:
            self.proxies.remove(proxy_str)
            self.failed_proxies.append(proxy_str)
            print(f"❌ Removed failed proxy: {proxy_str} (Remaining: {len(self.proxies)})")
    
    def get_stats(self) -> dict:
        """Thống kê proxy"""
        return {
            'total_loaded': len(self.proxies) + len(self.failed_proxies),
            'available': len(self.proxies),
            'failed': len(self.failed_proxies)
        }
    
    def reload_proxies(self):
        """Reload lại danh sách proxy từ file"""
        self.failed_proxies.clear()
        self.load_proxies()
        print(f"🔄 Reloaded proxies. Available: {len(self.proxies)}")
    
    def _test_single_proxy(self, proxy: str, timeout: int = 2) -> bool:
        """
        Test 1 proxy xem có hoạt động không
        
        Args:
            proxy: IP:PORT string
            timeout: Timeout cho test (giây)
        
        Returns:
            True nếu proxy hoạt động, False nếu không
        """
        test_url = "http://httpbin.org/ip"  # Fast test endpoint
        proxy_dict = {
            'http': f'http://{proxy}',
            'https': f'http://{proxy}'
        }
        
        try:
            response = requests.get(
                test_url, 
                proxies=proxy_dict, 
                timeout=timeout,
                verify=False
            )
            return response.status_code == 200
        except:
            return False
    
    def validate_proxies(self, 
                        max_workers: int = 50, 
                        timeout: int = 2,
                        test_limit: int = None,
                        save_to_file: bool = True) -> List[str]:
        """
        Validate danh sách proxy bằng cách test từng cái
        
        Args:
            max_workers: Số thread song song để test
            timeout: Timeout cho mỗi test (giây)
            test_limit: Giới hạn số proxy test (None = test all)
            save_to_file: Lưu danh sách proxy hợp lệ vào file
        
        Returns:
            List các proxy hợp lệ
        """
        print(f"\n🔍 Starting proxy validation...")
        print(f"Total proxies to test: {len(self.proxies)}")
        print(f"Workers: {max_workers}, Timeout: {timeout}s")
        
        # Giới hạn số lượng test nếu cần
        proxies_to_test = self.proxies[:test_limit] if test_limit else self.proxies
        
        working_proxies = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_proxy = {
                executor.submit(self._test_single_proxy, proxy, timeout): proxy 
                for proxy in proxies_to_test
            }
            
            # Process results với progress bar
            with tqdm(total=len(future_to_proxy), desc="Testing proxies") as pbar:
                for future in as_completed(future_to_proxy):
                    proxy = future_to_proxy[future]
                    try:
                        if future.result():
                            working_proxies.append(proxy)
                    except Exception as e:
                        pass  # Proxy failed
                    finally:
                        pbar.update(1)
                        pbar.set_postfix({"Working": len(working_proxies)})
        
        print(f"\n✅ Validation complete!")
        print(f"Working proxies: {len(working_proxies)}/{len(proxies_to_test)}")
        print(f"Success rate: {len(working_proxies)/len(proxies_to_test)*100:.1f}%")
        
        # Lưu vào file
        if save_to_file and working_proxies:
            with open(self.validated_file, 'w', encoding='utf-8') as f:
                for proxy in working_proxies:
                    f.write(f"{proxy}\n")
            print(f"💾 Saved {len(working_proxies)} working proxies to {self.validated_file.name}")
        
        # Update danh sách proxy hiện tại
        self.proxies = working_proxies
        
        return working_proxies
