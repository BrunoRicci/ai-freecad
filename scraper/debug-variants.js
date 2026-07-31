const fs = require('fs');
const { JSDOM } = require('jsdom');

console.log('Debugging data-variants...\n');

const html = fs.readFileSync('page.html', 'utf-8');
const url = 'https://www.batuk.com.ar/hombre/abrigos/';

const dom = new JSDOM(html, { url, pretendToBeVisual: true });
const document = dom.window.document;

const productElements = document.querySelectorAll('[data-variants]');
console.log(`Found ${productElements.length} elements with data-variants\n`);

// Check first element
if (productElements.length > 0) {
  const first = productElements[0];
  console.log('First element:');
  console.log('Tag:', first.tagName);
  console.log('Classes:', first.className);
  console.log('Parent tag:', first.parentElement?.tagName);
  console.log('Parent classes:', first.parentElement?.className);

  // Check for links
  const links = first.querySelectorAll('a');
  console.log(`\nFound ${links.length} links in element`);
  if (links.length > 0) {
    console.log('First link href:', links[0].href);
  }

  // Check for title elements
  const titles = first.querySelectorAll('h2, h3');
  console.log(`Found ${titles.length} title elements`);
  if (titles.length > 0) {
    console.log('First title:', titles[0].textContent.trim().substring(0, 50));
  }

  // Get variants data
  const variantsStr = first.getAttribute('data-variants');
  console.log(`\nVariants string length: ${variantsStr.length}`);

  try {
    const variants = JSON.parse(variantsStr);
    console.log('Parsed variants successfully');
    console.log('Number of variants:', Array.isArray(variants) ? variants.length : 'not an array');

    if (Array.isArray(variants) && variants[0]) {
      console.log('\nFirst variant keys:', Object.keys(variants[0]).slice(0, 10));
      console.log('price_short:', variants[0].price_short);
      console.log('image_url:', variants[0].image_url?.substring(0, 80));
    }
  } catch (e) {
    console.log('Failed to parse variants:', e.message);
  }

  // Check parent for link
  let parent = first.parentElement;
  let depth = 0;
  while (parent && depth < 5) {
    const links = parent.querySelectorAll(':scope > a');
    if (links.length > 0) {
      console.log(`\nFound link at parent depth ${depth}:`, links[0].href);
      break;
    }
    parent = parent.parentElement;
    depth++;
  }
}
