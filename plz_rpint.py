from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image as PILImage
import time, os, tempfile, random
import pyautogui
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Image, PageBreak
from reportlab.lib.pagesizes import letter

def main():
    urls = []
    preferences = setup_firefox()
    with open('put_urls_here.txt', 'r') as URL_file:
        for line in URL_file:
            current_url = line.strip()
            urls.append(current_url)
            print(current_url)
            collect_screenshots(current_url, preferences)
            print("Done with link!")
            split_to_pdfs(current_url)
    print("Thx")

def collect_screenshots(current_url, preferences):
    #Start up Firefox with specified preferences
    driver = webdriver.Firefox(options=preferences)

    # Calculate and set the desired window width based on half of the screen width
    screen_width = 1920
    window_height = 1080
    window_width = screen_width // 2
    driver.set_window_size(window_width, window_height)
    
    driver.get(current_url)

    # Scroll to the bottom of the page to ensure everything loads
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Create an ActionChains instance
    actions = ActionChains(driver)

    # Find the <body> element
    body_element = driver.find_element(By.TAG_NAME, "body")

    # Scroll to the element to make it visible
    driver.execute_script("arguments[0].scrollIntoView();", body_element)

    # Right-click on the element and navigate to "take screenshot" (8th option in context menu)
    actions.context_click(body_element).perform()
    time.sleep(2)
    pyautogui.press('down') #1
    pyautogui.press('down') #2
    pyautogui.press('down') #3
    pyautogui.press('down') #4
    pyautogui.press('down') #5
    pyautogui.press('down') #6
    pyautogui.press('down') #7
    pyautogui.press('down') #8
    pyautogui.press('enter') #select

    # Find and click the "Save full page" and "Download" buttons
    time.sleep(1)  # Wait a sec
    pyautogui.press('tab')
    pyautogui.press('enter')
    wait = WebDriverWait(driver, 10)
    iframe = wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'firefox-screenshots-preview-iframe')))
    download_button = driver.find_element(By.XPATH, "//button[@class='highlight-button-download']")
    download_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'highlight-button-download')))

    download_button.click()
    time.sleep(1)

    # Close the browser window
    driver.quit()

def setup_firefox():
    # Setting preferences for Firefox WebDriver with specified options
    options = Options()
    
    #Find where the temp_screenshots folder is on user's device and set as absolute path
    script_directory = os.path.dirname(os.path.abspath(__file__))
    download_dir = os.path.join(script_directory, "temp_screenshots")
    #options.add_argument('-headless') #delete the "#" before "options" on this line to enable headless mode!
    options.add_argument("--force-theme=light")
    options.set_preference("browser.download.folderList", 2);
    options.set_preference("browser.download.dir", download_dir)
    options.set_preference("browser.download.useDownloadDir", True);
    options.set_preference("browser.download.viewableInternally.enabledTypes", "");
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf;text/plain;application/text;text/xml;application/xml;image/png;image/jpeg");
    options.set_preference("pdfjs.disabled", True);
    options.set_preference("browser.download.useDownloadDir", True)

    return options

def split_to_pdfs(current_url):
    #Set input and output paths as absolutes
    script_directory = os.path.dirname(os.path.abspath(__file__))
    input_image_path = os.path.join(script_directory, "temp_screenshots")
    output_pdf_path = os.path.join(script_directory, "pickup_pdfs_here")

    # List all image files in the input folder
    image_files = [file for file in os.listdir(input_image_path) if file.lower().endswith(".png")]

    # Define the dimensions of the PDF page
    header_height = 50
    pdf_page_width, pdf_page_height = letter
    pdf_frame_width = pdf_page_width
    pdf_frame_height = pdf_page_height - header_height
    frame_margin = 12  # You might need to adjust this value

    # Process each image file
    for image_file in image_files:
        input_image = os.path.join(input_image_path, image_file)
        output_pdf = os.path.join(output_pdf_path, image_file.replace(".png", ".pdf"))  # Change this line

    # Load the input image
    pil_image = PILImage.open(input_image)
    image_width, image_height = pil_image.size

    # Create a temporary directory to store resized images
    temp_dir = tempfile.mkdtemp()

    # Resize the image to fit the PDF width while maintaining aspect ratio
    new_width = pdf_page_width - frame_margin
    new_height = int(image_height * (pdf_page_width / image_width))
    resized_image = pil_image.resize((int(new_width), int(new_height)), PILImage.Resampling.LANCZOS)

    # Calculate the number of sections needed
    num_sections = int(new_height / (pdf_frame_height)) + 1
    print('num_sections: ', num_sections)

    # Create a Frame for the header content
    header_frame = Frame(0, pdf_frame_height - header_height, pdf_frame_width + frame_margin, header_height + frame_margin)

    # Create a Frame for the main content (excluding header)
    main_content_frame = Frame(0, 0, pdf_frame_width + frame_margin, pdf_frame_height + frame_margin)  # Adjusted height

    # Create a Flowable container to hold the main content elements
    main_content = []

    # Define the header content
    def header(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 10)

        header_text = current_url
        max_text_width = pdf_frame_width - 2 * frame_margin

        lines = []
        current_line = ""

        for char in header_text:
            potential_line = f"{current_line}{char}"
            
            if canvas.stringWidth(potential_line) <= max_text_width:
                current_line = potential_line
            else:
                lines.append(current_line)
                current_line = char
        
        if current_line:
            lines.append(current_line)

        # Calculate the y-coordinate where the header text will start
        y_coordinate = pdf_page_height - header_height + 40

        for line in lines:
            canvas.drawString(20, y_coordinate, line)
            y_coordinate -= 12

        canvas.restoreState()

    print("Header Frame Dimensions:", header_frame._aW, "x", header_frame._aH)
    print("Main Content Frame Dimensions:", main_content_frame._aW, "x", main_content_frame._aH)

    # Create a PageTemplate with the header and main content frames
    combined_template = PageTemplate(frames=[header_frame, main_content_frame], onPage=header)

    # Build the PDF document using BaseDocTemplate
    doc = BaseDocTemplate(output_pdf, pagesize=(pdf_page_width, pdf_page_height), showBoundary=0)
    doc.addPageTemplates(combined_template)

    # Create a Frame for each section and add cropped images to the main content
    for section_num in range(num_sections):
        top = section_num * pdf_frame_height
        bottom = min(top + pdf_frame_height, new_height)
        
        # Calculate the actual height of the current section
        actual_section_height = bottom - top
        print("bottom", bottom, "top", top, "actual selection height", actual_section_height)
        
        # Crop the resized image section
        cropped_image = resized_image.crop((0, top, new_width, bottom))
        
        # Save the cropped image as a temporary file
        cropped_image_path = os.path.join(temp_dir, f'cropped_{section_num}.png')
        cropped_image.save(cropped_image_path)
        
        # Create a CustomImage object with the cropped image path
        custom_image = Image(cropped_image_path, width=pdf_frame_width, height=actual_section_height)
        main_content.append(custom_image)
        
        # Add a PageBreak except for the last section
        if section_num < num_sections - 1:
            main_content.append(PageBreak())

    # Build the PDF document
    doc.build(main_content)

    # Clean up temporary directory
    for filename in os.listdir(temp_dir):
        file_path = os.path.join(temp_dir, filename)
        os.remove(file_path)
    os.rmdir(temp_dir)

main()