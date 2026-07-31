const fs = require('fs');
const { JSDOM } = require('jsdom');

console.log('Working scraper - getting data from data-variants...\n');

const html = fs.readFileSync('page.html', 'utf-8');
const url = 'https://www.batuk.com.ar/hombre/abrigos/';

const dom = new JSDOM(html, { url, pretendToBeVisual: true });
const document = dom.window.document;
const products = [];

// Get all product items (the parent container)
const productItems = document.querySelectorAll('.js-item-product');
console.log(`Found ${productItems.length} product items\n`);

productItems.forEach((item, index) => {
  try {
    // Get title from item
    let title = null;
    const titleEl = item.querySelector('h2, h3');
    if (titleEl) {
      title = titleEl.textContent.trim();
    }

    // Get URL from first link
    let productUrl = null;
    const link = item.querySelector('a[href*="/productos/"]');
    if (link) {
      productUrl = link.href;
      if (!productUrl.startsWith('http')) {
        productUrl = new URL(productUrl, url).href;
      }
    }

    // Get variants data
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

            if (firstVariant.price_short) {
              price = firstVariant.price_short;
            }

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

    if (productUrl && title) {
      products.push({
        title,
        price,
        image,
        url: productUrl
      });
    }
  } catch (e) {
    console.error(`Error processing item ${index}:`, e.message);
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
    // Check if image URL is complete
    const imageDisplay = product.image.length > 70
      ? product.image.substring(0, 70) + '...'
      : product.image;
    console.log(`   Image: ✓ ${imageDisplay}`);
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
