const fs = require('fs');
const { JSDOM } = require('jsdom');

console.log('Perfect scraper - extracting from data-variants...\n');

const html = fs.readFileSync('page.html', 'utf-8');
const url = 'https://www.batuk.com.ar/hombre/abrigos/';

const dom = new JSDOM(html, { url, pretendToBeVisual: true });
const document = dom.window.document;
const products = [];

// Get all product containers with data-variants
const productElements = document.querySelectorAll('[data-variants]');
console.log(`Found ${productElements.length} products with variants data\n`);

productElements.forEach((element, index) => {
  try {
    // Get the data-variants attribute
    const variantsStr = element.getAttribute('data-variants');
    if (!variantsStr) return;

    let variants;
    try {
      variants = JSON.parse(variantsStr);
    } catch (e) {
      return; // Skip if can't parse
    }

    if (!Array.isArray(variants) || variants.length === 0) return;

    const firstVariant = variants[0];

    // Get price from variant
    let price = firstVariant.price_short || 'N/A';

    // Get image from variant
    let image = null;
    if (firstVariant.image_url) {
      image = firstVariant.image_url;
      if (!image.startsWith('http')) {
        image = 'https:' + image;
      }
    }

    // Get title and URL from the parent element's link
    const link = element.querySelector('a[href]');
    if (!link) return;

    let productUrl = link.href;
    if (!productUrl.startsWith('http')) {
      productUrl = new URL(productUrl, url).href;
    }

    // Get title
    let title = null;
    const titleEl = element.querySelector('h2, h3, [class*="title"]');
    if (titleEl) {
      title = titleEl.textContent.trim();
    }
    if (!title && link.textContent) {
      title = link.textContent.trim().split('\n')[0];
    }

    if (productUrl && title) {
      products.push({
        title,
        price,
        image,
        url: productUrl
      });
    }
  } catch (e) {
    console.error(`Error processing element ${index}:`, e.message);
  }
});

console.log(`Extracted ${products.length} products\n`);

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

console.log(`Unique products: ${uniqueProducts.length}\n`);

// Display results
uniqueProducts.forEach((product, index) => {
  console.log(`${index + 1}. ${product.title}`);
  console.log(`   Price: ${product.price}`);
  console.log(`   URL: ${product.url}`);
  if (product.image) {
    console.log(`   Image: ✓ ${product.image}`);
  } else {
    console.log(`   Image: N/A`);
  }
  console.log();
});

// Save to JSON
const outputData = {
  url: url,
  timestamp: new Date().toISOString(),
  totalProducts: uniqueProducts.length,
  products: uniqueProducts
};

fs.writeFileSync('batuk-products.json', JSON.stringify(outputData, null, 2));
console.log('✓ Saved batuk-products.json');

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
console.log('✓ Saved batuk-products.csv');
