const fs = require('fs');
const { JSDOM } = require('jsdom');

console.log('Final Batuk Scraper - Complete Data Extraction\n');
console.log('=' .repeat(50) + '\n');

const html = fs.readFileSync('page.html', 'utf-8');
const url = 'https://www.batuk.com.ar/hombre/abrigos/';

const dom = new JSDOM(html, { url, pretendToBeVisual: true });
const document = dom.window.document;
const products = [];

// Get all product items
const productItems = document.querySelectorAll('.js-item-product');
console.log(`Found ${productItems.length} product items\n`);

productItems.forEach((item, index) => {
  try {
    // Get URL from link
    let productUrl = null;
    const link = item.querySelector('a[href*="/productos/"]');
    if (!link) return;

    productUrl = link.href;
    if (!productUrl.startsWith('http')) {
      productUrl = new URL(productUrl, url).href;
    }

    // Get title from link's title attribute or img alt
    let title = null;
    if (link.title) {
      title = link.title.trim();
    } else {
      const img = item.querySelector('img');
      if (img && img.alt) {
        title = img.alt.split(' - ')[0].trim(); // Take first part before " - "
      }
    }

    if (!title) return; // Skip if no title found

    // Get variants data for price and image
    let price = 'N/A';
    let image = null;

    const variantsContainer = item.querySelector('[data-variants]');
    if (variantsContainer) {
      const variantsStr = variantsContainer.getAttribute('data-variants');
      if (variantsStr) {
        try {
          const variants = JSON.parse(variantsStr);
          if (Array.isArray(variants) && variants.length > 0) {
            const firstVariant = variants[0];

            // Get price
            if (firstVariant.price_short) {
              price = firstVariant.price_short;
            }

            // Get image
            if (firstVariant.image_url) {
              image = firstVariant.image_url;
              if (!image.startsWith('http')) {
                image = 'https:' + image;
              }
            }
          }
        } catch (e) {
          // Skip if parse fails
        }
      }
    }

    products.push({
      title,
      price,
      image,
      url: productUrl
    });

  } catch (e) {
    // Skip on error
  }
});

console.log(`Extracted ${products.length} products\n`);

// Deduplicate by URL, keeping best data
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

console.log(`Final count: ${uniqueProducts.length} unique products\n`);
console.log('=' .repeat(50) + '\n');

// Display results
uniqueProducts.forEach((product, index) => {
  console.log(`${index + 1}. ${product.title}`);
  console.log(`   Price: ${product.price}`);
  console.log(`   URL: ${product.url}`);
  console.log(`   Image: ${product.image ? '✓ Loaded' : '✗ Not found'}`);
  console.log();
});

console.log('=' .repeat(50) + '\n');

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

console.log('✓ Saved batuk-products.json');
console.log('✓ Saved batuk-products.csv');
console.log('\nFiles ready for download!');
