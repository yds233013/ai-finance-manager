import pytesseract
from PIL import Image
import io
import re
from typing import Dict, List, Optional
from datetime import datetime

class ReceiptProcessor:
    def __init__(self):
        self.date_patterns = [
            r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
            r'\d{2}-\d{2}-\d{4}',  # MM-DD-YYYY
            r'\d{4}/\d{2}/\d{2}',  # YYYY/MM/DD
            r'\d{4}-\d{2}-\d{2}'   # YYYY-MM-DD
        ]
        
        self.amount_pattern = r'\$?\d+\.\d{2}'
    
    async def process_image(self, image_bytes: bytes) -> Dict:
        """
        Process a receipt image and extract relevant information.
        """
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_bytes))
            
            # Extract text from image
            text = pytesseract.image_to_string(image)
            
            # Process extracted text
            result = {
                "date": self._extract_date(text),
                "total_amount": self._extract_total(text),
                "items": self._extract_items(text),
                "merchant": self._extract_merchant(text),
                "raw_text": text
            }
            
            return result
        
        except Exception as e:
            print(f"Error processing receipt: {e}")
            return {
                "error": "Failed to process receipt",
                "details": str(e)
            }
    
    def _extract_date(self, text: str) -> Optional[str]:
        """Extract date from receipt text."""
        for pattern in self.date_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    date_str = match.group(0)
                    # Convert to consistent format (YYYY-MM-DD)
                    if '/' in date_str:
                        parts = date_str.split('/')
                    else:
                        parts = date_str.split('-')
                    
                    if len(parts[0]) == 4:  # YYYY-MM-DD
                        return date_str
                    else:  # MM-DD-YYYY
                        return f"{parts[2]}-{parts[0]}-{parts[1]}"
                except:
                    continue
        return None
    
    def _extract_total(self, text: str) -> Optional[float]:
        """Extract total amount from receipt text."""
        # Look for common total indicators
        total_indicators = ['TOTAL', 'Total:', 'Amount Due:', 'AMOUNT']
        lines = text.split('\n')
        
        for line in lines:
            if any(indicator in line.upper() for indicator in total_indicators):
                matches = re.findall(self.amount_pattern, line)
                if matches:
                    try:
                        # Take the last amount in the line
                        amount = float(matches[-1].replace('$', ''))
                        return amount
                    except:
                        continue
        
        # If no total found with indicators, take the largest amount
        amounts = []
        for line in lines:
            matches = re.findall(self.amount_pattern, line)
            for match in matches:
                try:
                    amounts.append(float(match.replace('$', '')))
                except:
                    continue
        
        return max(amounts) if amounts else None
    
    def _extract_items(self, text: str) -> List[Dict]:
        """Extract individual items from receipt text."""
        items = []
        lines = text.split('\n')
        
        for line in lines:
            # Skip empty lines and common headers
            if not line.strip() or any(h in line.upper() for h in ['TOTAL', 'SUBTOTAL', 'TAX', 'DATE', 'TIME']):
                continue
            
            # Look for lines with amounts
            matches = re.findall(self.amount_pattern, line)
            if matches:
                try:
                    amount = float(matches[-1].replace('$', ''))
                    # Remove the amount from the line to get the description
                    description = line.replace(matches[-1], '').strip()
                    if description:
                        items.append({
                            "description": description,
                            "amount": amount
                        })
                except:
                    continue
        
        return items
    
    def _extract_merchant(self, text: str) -> Optional[str]:
        """Extract merchant name from receipt text."""
        lines = text.split('\n')
        # Usually the merchant name is in the first few lines
        for line in lines[:5]:
            line = line.strip()
            if line and len(line) > 3 and not any(c.isdigit() for c in line):
                return line
        return None

    def enhance_image(self, image_bytes: bytes) -> bytes:
        """
        Enhance receipt image for better OCR results
        """
        try:
            # Open image
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to grayscale
            image = image.convert('L')
            
            # Increase contrast
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)
            
            # Save enhanced image to bytes
            output = io.BytesIO()
            image.save(output, format='PNG')
            return output.getvalue()
            
        except Exception as e:
            raise Exception(f"Image enhancement failed: {str(e)}") 