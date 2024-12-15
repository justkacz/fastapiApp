print('Start #################################################################');

db = db.getSiblingDB("booksdb");

db.books.insertMany([
    { title: 'Book1', author: 'Author1', description: 'd1', username: 'justkacz@wp.pl' },
    { title: 'Book2', author: 'Author2', description: 'd2', username: 'justkacz2' },
    { title: 'Book3', author: 'Author3', description: 'd3', username: 'justkacz3' },
    { title: 'Book4', author: 'Author4', description: 'd4', username: 'justkacz@wp.pl' }
])