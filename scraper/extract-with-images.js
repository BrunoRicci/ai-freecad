const fs = require('fs');

console.log('Reading existing data and enriching with images...\n');

// Read the HTML we already fetched
const html = fs.readFileSync('page.html', 'utf-8');

// Read the existing JSON with product data
const existingData = JSON.parse(fs.readFileSync('batuk-products.json', 'utf-8'));

// Extract all product image URLs from HTML
const imageUrls = [];
const imageRegex = /https:\/\/acdn[^"]*\.webp/g;
let match;
while ((match = imageRegex.exec(html)) !== null) {
  imageUrls.push(match[0]);
}

// Remove duplicates
const uniqueImages = [...new Set(imageUrls)];
console.log(`Found ${uniqueImages.length} unique image URLs\n`);

// Create a mapping of product names to images (first pass - simple heuristic)
const productTitles = existingData.products.map(p => p.title.toLowerCase());

// Try to match images to products
const imageMap = {};

productTitles.forEach((title, idx) => {
  // Extract key words from title
  const words = title.replace(/ - comprar online/i, '').toLowerCase().split(/[\s\-]+/);

  // Find best matching image
  const matched = uniqueImages.find(img => {
    const imgLower = img.toLowerCase();
    // Check if product name is in image URL
    return words.some(word => word && imgLower.includes(word.substring(0, 3)));
  });

  if (matched) {
    imageMap[idx] = matched;
  }
});

// Update products with images
let imagesAdded = 0;
existingData.products.forEach((product, idx) => {
  if (imageMap[idx] && !product.image) {
    product.image = imageMap[idx];
    imagesAdded++;
  } else if (!product.image) {
    // Try to find image by product name in URL
    const productId = product.url.split('/').pop().toLowerCase().replace(/\/$/, '');
    const imagesByName = uniqueImages.filter(img =>
      img.toLowerCase().includes(productId.substring(0, 5))
    );
    if (imagesByName.length > 0) {
      product.image = imagesByName[0];
      imagesAdded++;
    }
  }
});

console.log(`Added/Updated ${imagesAdded} product images`);
console.log('\nUpdated product list:\n');

existingData.products.forEach((product, index) => {
  console.log(`${index + 1}. ${product.title}`);
  console.log(`   Price: ${product.price}`);
  console.log(`   URL: ${product.url}`);
  console.log(`   Image: ${product.image || 'N/A'}\n`);
});

// Save updated data
fs.writeFileSync('batuk-products.json', JSON.stringify(existingData, null, 2));

// Generate CSV
const csv = [
  ['Title', 'Price', 'URL', 'Image'].join(',')
].concat(
  existingData.products.map(p => [
    `"${(p.title || '').replace(/"/g, '""')}"`,
    `"${(p.price || '').replace(/"/g, '""')}"`,
    `"${(p.url || '').replace(/"/g, '""')}"`,
    `"${(p.image || '').replace(/"/g, '""')}"`
  ].join(','))
).join('\n');

fs.writeFileSync('batuk-products.csv', csv);

console.log('Updated batuk-products.json');
console.log('Updated batuk-products.csv');
