const fs = require('fs');
const { JSDOM } = require('jsdom');

const html = fs.readFileSync('page.html', 'utf-8');
const url = 'https://www.batuk.com.ar/hombre/abrigos/';

const dom = new JSDOM(html, { url, pretendToBeVisual: true });
const document = dom.window.document;

const productItems = document.querySelectorAll('.js-item-product');
const item = productItems[0];

// Check all attributes
console.log('All element attributes:');
for (let element of item.querySelectorAll('*')) {
  const tagName = element.tagName.toLowerCase();

  // Look for title-like content
  if (element.title) console.log(`  ${tagName}.title: "${element.title}"`);
  if (element.alt) console.log(`  ${tagName}.alt: "${element.alt}"`);
  if (element.textContent?.trim() && element.textContent.length < 100 && element.textContent.length > 3) {
    const cleanText = element.textContent.trim().replace(/\s+/g, ' ');
    if (cleanText.includes('Campera') || cleanText.includes('Botan')) {
      console.log(`  ${tagName}: "${cleanText}"`);
    }
  }

  // Check data attributes
  const attrs = element.attributes;
  for (let attr of attrs) {
    if (attr.name.includes('data') || attr.name.includes('title') || attr.name.includes('name')) {
      if (attr.value.length < 100) {
        console.log(`  ${tagName}[${attr.name}]: "${attr.value}"`);
      }
    }
  }
}

// Also check for the product name in links
console.log('\nProduct link analysis:');
const link = item.querySelector('a[href*="/productos/"]');
if (link) {
  console.log('Link href:', link.href);
  console.log('Link text:', link.textContent.trim().substring(0, 100));
  console.log('Link title attr:', link.title);

  // Extract name from URL
  const urlParts = link.href.split('/');
  const productName = urlParts[urlParts.length - 1].replace(/\/$/, '');
  console.log('Product name from URL:', productName);
}
