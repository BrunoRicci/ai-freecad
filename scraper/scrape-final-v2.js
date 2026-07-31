const fs = require('fs');

console.log('Scraping Batuk with image extraction from data-variants...\n');

const html = fs.readFileSync('page.html', 'utf-8');
const url = 'https://www.batuk.com.ar/hombre/abrigos/';
const products = [];

// Parse using regex to extract product data
const productRegex = /data-store="(product-item-[^"]*)"/g;
let match;

while ((match = productRegex.exec(html)) !== null) {
  const productStoreId = match[1];
  const searchStart = match.index;

  // Find the product container - look backwards and forwards for relevant data
  let startIndex = Math.max(0, searchStart - 3000);
  let endIndex = Math.min(html.length, searchStart + 5000);

  const section = html.substring(startIndex, endIndex);

  // Extract URL
  const urlMatch = section.match(/href="([^"]*?\/productos\/[^"]*?)"/);
  if (!urlMatch) continue;

  let productUrl = urlMatch[1];
  if (!productUrl.startsWith('http')) {
    productUrl = productUrl.startsWith('/')
      ? 'https://www.batuk.com.ar' + productUrl
      : new URL(productUrl, url).href;
  }

  // Extract title - look for h2 or text near the product
  let title = null;
  const titleMatch = section.match(/<h2[^>]*>([^<]+)<\/h2>/);
  if (titleMatch) {
    title = titleMatch[1].trim();
  }
  if (!title) {
    const titleAltMatch = section.match(/<h3[^>]*>([^<]+)<\/h3>/);
    if (titleAltMatch) {
      title = titleAltMatch[1].trim();
    }
  }

  // Extract image from data-variants JSON
  let image = null;
  const variantsMatch = section.match(/data-variants="(\[.*?\])"/);
  if (variantsMatch) {
    try {
      const variantsJson = variantsMatch[1]
        .replace(/&quot;/g, '"')
        .replace(/&#039;/g, "'")
        .replace(/&amp;/g, '&');

      const variants = JSON.parse(variantsJson);
      if (variants.length > 0 && variants[0].image_url) {
        image = variants[0].image_url;
        if (!image.startsWith('http')) {
          image = 'https:' + image;
        }
      }
    } catch (e) {
      // Skip if JSON parsing fails
    }
  }

  // Extract price from data-variants
  let price = null;
  if (variantsMatch) {
    try {
      const variantsJson = variantsMatch[1]
        .replace(/&quot;/g, '"')
        .replace(/&#039;/g, "'")
        .replace(/&amp;/g, '&');

      const variants = JSON.parse(variantsJson);
      if (variants.length > 0 && variants[0].price_short) {
        price = variants[0].price_short;
      }
    } catch (e) {
      // Skip if JSON parsing fails
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
}

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
  console.log(`   Image: ${product.image ? '✓ ' + product.image.substring(0, 60) + '...' : 'N/A'}\n`);
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

console.log('✓ Saved batuk-products.json');
console.log('✓ Saved batuk-products.csv');
