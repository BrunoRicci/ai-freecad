const fs = require('fs');
const { JSDOM } = require('jsdom');

console.log('Final scrape with improved image extraction...\n');

const html = fs.readFileSync('page.html', 'utf-8');
const url = 'https://www.batuk.com.ar/hombre/abrigos/';

const dom = new JSDOM(html, { url, pretendToBeVisual: true });
const document = dom.window.document;
const products = [];

// Get all product containers
const productElements = document.querySelectorAll('[data-store^="product-item-"]');
console.log(`Found ${productElements.length} product elements\n`);

productElements.forEach((element, index) => {
  try {
    // Get URL
    const link = element.querySelector('a[href]');
    if (!link) return;

    let productUrl = link.href;
    if (!productUrl.startsWith('http')) {
      productUrl = new URL(productUrl, url).href;
    }

    // Get ALL images in this product element
    let image = null;
    const imgElements = element.querySelectorAll('img');

    for (let img of imgElements) {
      // Get the src or data-src
      let src = img.src;

      // Check for actual image URLs first
      if (src && src.includes('acdn') && src.includes('.webp')) {
        image = src;
        break;
      }

      // Then check data-src
      const dataSrc = img.getAttribute('data-src');
      if (dataSrc && dataSrc.includes('acdn') && dataSrc.includes('.webp')) {
        image = dataSrc;
        break;
      }
    }

    // If still no image, look in the entire element's HTML for image URLs
    if (!image) {
      const elementHtml = element.innerHTML;
      const imageMatch = elementHtml.match(/https:\/\/acdn[^"]*\.webp/);
      if (imageMatch) {
        image = imageMatch[0];
      }
    }

    // Get title
    let title = null;
    const titleEl = element.querySelector('h2, h3, [class*="title"]');
    if (titleEl) {
      title = titleEl.textContent.trim();
    }
    if (!title) {
      // Look for any text content that might be a title
      const allText = element.textContent.trim().split('\n')[0];
      if (allText && allText.length > 5) {
        title = allText;
      }
    }

    // Get price
    let price = null;
    const priceEl = element.querySelector('[class*="price"], .precio, [data-testid*="price"]');
    if (priceEl) {
      const text = priceEl.textContent.trim();
      const match = text.match(/\$[\d.,]+/);
      if (match) {
        price = match[0];
      }
    }

    if (productUrl && title) {
      products.push({
        title,
        price: price || 'N/A',
        image: image || null,
        url: productUrl
      });
    }
  } catch (e) {
    console.error(`Error processing element ${index}:`, e.message);
  }
});

// Deduplicate
const uniqueMap = new Map();
products.forEach(product => {
  const existing = uniqueMap.get(product.url);
  if (!existing ||
      (product.price !== 'N/A' && existing.price === 'N/A') ||
      (product.image && !existing.image)) {
    uniqueMap.set(product.url, product);
  }
});

const uniqueProducts = Array.from(uniqueMap.values());

console.log(`Extracted ${products.length} products (${uniqueProducts.length} unique)\n`);

uniqueProducts.forEach((product, index) => {
  console.log(`${index + 1}. ${product.title}`);
  console.log(`   Price: ${product.price}`);
  console.log(`   URL: ${product.url}`);
  console.log(`   Image: ${product.image ? '✓ Found' : 'N/A'}\n`);
});

// Save to JSON
const outputData = {
  url: url,
  timestamp: new Date().toISOString(),
  totalProducts: uniqueProducts.length,
  products: uniqueProducts
};

fs.writeFileSync('batuk-products.json', JSON.stringify(outputData, null, 2));

// Save to CSV
const csv = [
  ['Title', 'Price', 'URL', 'Image'].join(',')
].concat(
  uniqueProducts.map(p => [
    `"${(p.title || '').replace(/"/g, '""')}"`,
    `"${(p.price || '').replace(/"/g, '""')}"`,
    `"${(p.url || '').replace(/"/g, '""')}"`,
    `"${(p.image || '').replace(/"/g, '""')}"`
  ].join(','))
).join('\n');

fs.writeFileSync('batuk-products.csv', csv);

console.log('✓ Data saved to batuk-products.json');
console.log('✓ Data saved to batuk-products.csv');
