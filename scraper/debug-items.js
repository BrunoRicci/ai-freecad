const fs = require('fs');
const { JSDOM } = require('jsdom');

const html = fs.readFileSync('page.html', 'utf-8');
const url = 'https://www.batuk.com.ar/hombre/abrigos/';

const dom = new JSDOM(html, { url, pretendToBeVisual: true });
const document = dom.window.document;

const productItems = document.querySelectorAll('.js-item-product');
console.log(`Found ${productItems.length} product items\n`);

if (productItems.length > 0) {
  const item = productItems[0];

  console.log('Item element structure:');
  console.log('Tag:', item.tagName);
  console.log('Classes:', item.className);

  // Check for titles
  const h2 = item.querySelector('h2');
  const h3 = item.querySelector('h3');
  console.log('\nTitle elements:');
  console.log('h2:', h2 ? h2.textContent.trim().substring(0, 50) : 'NOT FOUND');
  console.log('h3:', h3 ? h3.textContent.trim().substring(0, 50) : 'NOT FOUND');

  // Check for links
  const links = item.querySelectorAll('a[href]');
  console.log(`\nLinks found: ${links.length}`);
  for (let i = 0; i < Math.min(3, links.length); i++) {
    console.log(`  Link ${i}: ${links[i].href}`);
  }

  // Look deeper
  console.log('\nAll text content (first 200 chars):');
  console.log(item.textContent.trim().substring(0, 200));

  // Check HTML structure
  console.log('\nHTML structure (first 500 chars):');
  console.log(item.innerHTML.substring(0, 500));
}
