from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import json
from datetime import datetime
import platform
import sys

# Month number to name mapping
MONTHS = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December"
}

class ProvenanceLogger:
    """Class to handle provenance logging"""
    
    def __init__(self, log_dir):
        self.log_dir = log_dir
        self.log_file = os.path.join(log_dir, f"provenance_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        self.session_log = {
            "session_info": {
                "start_time": datetime.now().isoformat(),
                "script_version": "1.0",
                "python_version": sys.version,
                "platform": platform.platform(),
                "source_url": "https://www.transtats.bts.gov/DL_SelectFields.aspx?gnoyr_VQ=FGJ&QO_fu146_anzr=b0-gvzr",
                "data_source": "Bureau of Transportation Statistics (BTS)",
                "dataset": "On-Time Performance"
            },
            "downloads": []
        }
    
    def log_download(self, year, month, fields_selected, status, error_message=None, 
                     download_filename=None, file_size=None):
        """Log a single download attempt"""
        download_entry = {
            "timestamp": datetime.now().isoformat(),
            "year": year,
            "month": month,
            "month_name": MONTHS[month],
            "fields_selected": fields_selected,
            "num_fields": len(fields_selected),
            "status": status,
            "download_filename": download_filename,
            "file_size_bytes": file_size,
            "error_message": error_message
        }
        self.session_log["downloads"].append(download_entry)
        self._save_log()
    
    def log_session_end(self, total_success, total_failed):
        """Log session summary at the end"""
        self.session_log["session_info"]["end_time"] = datetime.now().isoformat()
        self.session_log["session_info"]["total_downloads_attempted"] = total_success + total_failed
        self.session_log["session_info"]["successful_downloads"] = total_success
        self.session_log["session_info"]["failed_downloads"] = total_failed
        self._save_log()
        self._create_summary_file(total_success, total_failed)
    
    def _save_log(self):
        """Save the current log to file"""
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(self.session_log, f, indent=2, ensure_ascii=False)
    
    def _create_summary_file(self, total_success, total_failed):
        """Create a human-readable summary file"""
        summary_file = os.path.join(self.log_dir, f"download_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("="*70 + "\n")
            f.write("BTS DATA DOWNLOAD PROVENANCE SUMMARY\n")
            f.write("="*70 + "\n\n")
            
            f.write(f"Download Session: {self.session_log['session_info']['start_time']}\n")
            f.write(f"Data Source: {self.session_log['session_info']['data_source']}\n")
            f.write(f"Source URL: {self.session_log['session_info']['source_url']}\n")
            f.write(f"Dataset: {self.session_log['session_info']['dataset']}\n\n")
            
            f.write(f"Total Downloads Attempted: {total_success + total_failed}\n")
            f.write(f"Successful: {total_success}\n")
            f.write(f"Failed: {total_failed}\n\n")
            
            f.write("="*70 + "\n")
            f.write("DOWNLOAD DETAILS\n")
            f.write("="*70 + "\n\n")
            
            for download in self.session_log["downloads"]:
                status_symbol = "✓" if download["status"] == "success" else "✗"
                f.write(f"{status_symbol} {download['year']}-{download['month_name']}\n")
                f.write(f"   Time: {download['timestamp']}\n")
                f.write(f"   Status: {download['status']}\n")
                f.write(f"   Fields Selected: {download['num_fields']}\n")
                
                if download['download_filename']:
                    f.write(f"   Filename: {download['download_filename']}\n")
                if download['file_size_bytes']:
                    f.write(f"   File Size: {download['file_size_bytes']:,} bytes\n")
                if download['error_message']:
                    f.write(f"   Error: {download['error_message']}\n")
                
                f.write("\n")
            
            f.write("="*70 + "\n")
            f.write("FIELDS SELECTED FOR ALL DOWNLOADS\n")
            f.write("="*70 + "\n\n")
            
            if self.session_log["downloads"]:
                fields = self.session_log["downloads"][0]["fields_selected"]
                for i, field in enumerate(fields, 1):
                    f.write(f"{i}. {field}\n")
        
        print(f"\n✓ Summary saved to: {summary_file}")

def setup_driver(download_dir):
    """Set up Chrome driver with download preferences - ENHANCED VERSION"""
    chrome_options = webdriver.ChromeOptions()
    
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-popup-blocking')
    chrome_options.add_argument('--disable-notifications')
    chrome_options.add_argument('--disable-infobars')
    
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": False,
        "safebrowsing.disable_download_protection": True,
        "profile.default_content_setting_values.automatic_downloads": 1,
        "profile.default_content_settings.popups": 0,
        "profile.content_settings.exceptions.automatic_downloads.*.setting": 1,
        "plugins.always_open_pdf_externally": True,
        "profile.default_content_setting_values.notifications": 2,
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False
    }
    
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    driver.execute_cdp_cmd("Page.setDownloadBehavior", {
        "behavior": "allow",
        "downloadPath": download_dir
    })
    
    return driver

def select_specific_fields(driver, desired_fields):
    """Select only specific checkboxes based on their labels - RETURNS selected fields list"""
    try:
        time.sleep(3)
        
        checkboxes = driver.find_elements(By.XPATH, "//input[@type='checkbox']")
        
        print(f"Found {len(checkboxes)} total checkboxes")
        selected_count = 0
        selected_fields = []
        
        for checkbox in checkboxes:
            try:
                checkbox_id = checkbox.get_attribute("id")
                checkbox_name = checkbox.get_attribute("name")
                checkbox_value = checkbox.get_attribute("value")
                
                label_text = ""
                try:
                    if checkbox_id:
                        label = driver.find_element(By.XPATH, f"//label[@for='{checkbox_id}']")
                        label_text = label.text.strip()
                except:
                    try:
                        label = checkbox.find_element(By.XPATH, "./ancestor::label")
                        label_text = label.text.strip()
                    except:
                        pass
                
                should_select = False
                for desired in desired_fields:
                    if desired.lower() in label_text.lower() or \
                       desired.lower() in str(checkbox_value).lower() or \
                       desired.lower() in str(checkbox_name).lower() or \
                       desired.lower() in str(checkbox_id).lower():
                        should_select = True
                        break
                
                if should_select and not checkbox.is_selected():
                    driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
                    time.sleep(0.1)
                    driver.execute_script("arguments[0].click();", checkbox)
                    selected_count += 1
                    field_name = label_text or checkbox_value or checkbox_name or checkbox_id
                    selected_fields.append(field_name)
                    print(f"  ✓ Selected: {field_name}")
                    
            except Exception as e:
                continue
        
        print(f"Selected {selected_count} checkboxes")
        return True, selected_fields
        
    except Exception as e:
        print(f"Error selecting checkboxes: {e}")
        return False, []

def wait_for_download_complete(download_dir, files_before, timeout=120):
    """Wait for download to complete - IMPROVED VERSION"""
    print("Waiting for download to start and complete...")
    start_time = time.time()
    download_started = False
    
    while time.time() - start_time < timeout:
        elapsed = int(time.time() - start_time)
        
        # Check for .crdownload files (download in progress)
        crdownload_files = [f for f in os.listdir(download_dir) if f.endswith('.crdownload')]
        
        if crdownload_files and not download_started:
            print(f"  Download started! ({elapsed}s)")
            download_started = True
        
        if crdownload_files:
            # Download still in progress
            print(f"  Download in progress... ({elapsed}s elapsed)")
            time.sleep(2)
            continue
        
        # No .crdownload files - check if new files appeared
        files_after = set(os.listdir(download_dir))
        new_files = files_after - files_before
        new_files = [f for f in new_files if not f.endswith('.crdownload') and not f.endswith('.tmp')]
        
        if new_files:
            print(f"  Download complete! ({elapsed}s total)")
            return True, new_files[0]
        
        # If download hasn't started yet, keep waiting
        if not download_started:
            print(f"  Waiting for download to start... ({elapsed}s elapsed)")
            time.sleep(2)
        else:
            # Download started but no new files yet - give it a bit more time
            time.sleep(2)
            # Check one more time
            files_after = set(os.listdir(download_dir))
            new_files = files_after - files_before
            new_files = [f for f in new_files if not f.endswith('.crdownload') and not f.endswith('.tmp')]
            if new_files:
                return True, new_files[0]
            
    print(f"  Warning: Download timeout reached after {timeout}s")
    
    # One last check for new files
    files_after = set(os.listdir(download_dir))
    new_files = files_after - files_before
    new_files = [f for f in new_files if not f.endswith('.crdownload') and not f.endswith('.tmp')]
    
    if new_files:
        print(f"  Found file after timeout: {new_files[0]}")
        return True, new_files[0]
    
    # Debug: show what files are in the directory
    print(f"  Files in directory: {list(os.listdir(download_dir))}")
    print(f"  Files before: {files_before}")
    
    return False, None

def download_data(driver, year, month, fields_to_select, provenance_logger, download_dir):
    """Download data for a specific year and month"""
    error_message = None
    selected_fields = []
    download_filename = None
    file_size = None
    
    try:
        # Get list of files before download - exclude temp files
        all_files = os.listdir(download_dir)
        files_before = set([f for f in all_files if not f.endswith('.crdownload') and not f.endswith('.tmp')])
        
        print(f"Files before download: {len(files_before)}")

        url = "https://www.transtats.bts.gov/DL_SelectFields.aspx?gnoyr_VQ=FGJ&QO_fu146_anzr=b0-gvzr"
        print(f"Loading page...")
        driver.get(url)
        time.sleep(5)
        
        month_name = MONTHS[month]
        
        print(f"Selecting year: {year}")
        year_dropdown = Select(WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "cboYear"))
        ))
        year_dropdown.select_by_visible_text(str(year))
        time.sleep(2)
        
        print(f"Selecting month: {month_name}")
        month_dropdown = Select(WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "cboPeriod"))
        ))
        month_dropdown.select_by_visible_text(month_name)
        time.sleep(2)
        
        # Select specific fields
        print("Selecting specific fields...")
        success, selected_fields = select_specific_fields(driver, fields_to_select)
        if not success:
            error_message = "Could not select fields"
            print(f"Warning: {error_message}")
        
        print("Looking for download button...")
        download_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.ID, "btnDownload"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", download_button)
        time.sleep(1)
        download_button.click()
        print(f"Clicked download button for {year}-{month_name}")
        
        # Wait for download to complete with better detection
        download_success, download_filename = wait_for_download_complete(download_dir, files_before, timeout=120)
        
        if download_success and download_filename:
            file_path = os.path.join(download_dir, download_filename)
            file_size = os.path.getsize(file_path)
            print(f"✓ Downloaded: {download_filename} ({file_size:,} bytes)")
        else:
            error_message = "No file downloaded - check download folder manually"
            print(f"Warning: {error_message}")
            # Check if file was actually downloaded despite detection failing
            all_files_after = os.listdir(download_dir)
            files_after = set([f for f in all_files_after if not f.endswith('.crdownload') and not f.endswith('.tmp')])
            new_files = files_after - files_before
            if new_files:
                download_filename = list(new_files)[0]
                file_path = os.path.join(download_dir, download_filename)
                file_size = os.path.getsize(file_path)
                print(f"  Actually found file: {download_filename} ({file_size:,} bytes)")
                error_message = None

        # Log the attempt
        provenance_logger.log_download(
            year=year,
            month=month,
            fields_selected=selected_fields,
            status="success" if download_filename else "failed",
            download_filename=download_filename,
            file_size=file_size,
            error_message=error_message
        )

        return download_filename is not None
        
    except Exception as e:
        error_message = str(e)
        print(f"Error downloading data for {year}-{MONTHS[month]}: {error_message}")
        import traceback
        traceback.print_exc()

        provenance_logger.log_download(
            year=year,
            month=month,
            fields_selected=selected_fields,
            status="failed",
            error_message=error_message
        )
        
        return False

def main():
    download_dir = os.path.join(os.getcwd(), "bts_downloads")
    os.makedirs(download_dir, exist_ok=True)
    
    # DEFINE YOUR DESIRED FIELDS HERE
    fields_to_select = [
        "chkDownloadZip"  # This will download as ZIP format
    ]
    
    print(f"Files will be downloaded to: {download_dir}")
    print(f"Will select these fields: {fields_to_select}")

    provenance_logger = ProvenanceLogger(download_dir)
    
    driver = setup_driver(download_dir)
    driver.maximize_window()

    total_success = 0
    total_failed = 0
    
    try:
        print("\n" + "="*50)
        print("TESTING WITH JANUARY 2023 FIRST")
        print("="*50)
        
        success = download_data(driver, 2023, 1, fields_to_select, provenance_logger, download_dir)
        
        if success:
            total_success += 1
            print(f"✓ Test successful!")
            print("\nTest download complete. Check the bts_downloads folder.")
            print("Press Enter to continue with all months, or Ctrl+C to stop...")
            input()
            
            for year in range(2023, 2026):
                first_month = 1 if year == 2023 else 1
                last_month = 11 if year == 2025 else 12
                
                for month in range(first_month, last_month + 1):
                    if year == 2023 and month == 1:
                        continue
                    
                    print(f"\n{'='*50}")
                    print(f"Processing: {year}-{MONTHS[month]}")
                    print(f"{'='*50}")
                    
                    success = download_data(driver, year, month, fields_to_select, provenance_logger, download_dir)
                    
                    if success:
                        total_success += 1
                        print(f"✓ Successfully processed {year}-{MONTHS[month]}")
                    else:
                        total_failed += 1
                        print(f"✗ Failed to process {year}-{MONTHS[month]}")
                    
                    # Longer pause between downloads
                    time.sleep(5)
        else:
            total_failed += 1
            print(f"✗ Test failed - but check the download folder to see if file is there")
        
        print("\n" + "="*50)
        print("Download process completed!")
        print(f"Successful: {total_success}")
        print(f"Failed: {total_failed}")
        print(f"Check {download_dir} for your files")
        print("="*50)
        
    except KeyboardInterrupt:
        print("\nProcess interrupted by user")
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        provenance_logger.log_session_end(total_success, total_failed)
        
        print("Waiting 10 seconds before closing browser...")
        time.sleep(10)
        driver.quit()

if __name__ == "__main__":
    main()