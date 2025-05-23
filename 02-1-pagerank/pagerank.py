import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    prob = dict()
    if len(corpus[page]) == 0:
        for p in corpus:
            prob[p]=1/len(corpus)
            return prob
    else:
        for p in corpus:
            prob[p]= (1-damping_factor)/len(corpus)
        for p in corpus[page]:
            prob[p] += damping_factor / len(corpus[page])
        return prob
    raise NotImplementedError


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    prob = dict()
    for p in corpus:
        prob[p] = 0 
    currentp = random.choice(list(corpus.keys()))
    for i in range(n):
        prob[currentp]  += 1 / n
        if random.random() < damping_factor:  
            if corpus[currentp]:  
                currentp = random.choice(list(corpus[currentp]))
            else:  
                currentp = random.choice(list(corpus.keys()))
        else:  
            currentp = random.choice(list(corpus.keys()))
    return prob


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    prob = dict()
    for p in corpus:
        prob[p] = 1 / len(corpus)
        for p in corpus:
            if len(corpus[p]) == 0:
                corpus[p] = set(corpus.keys())
    while True:
        newprob = dict()
        for p in corpus:
            newprob[p] = (1 - damping_factor) / len(corpus) + damping_factor * sum(prob[i] / len(corpus[i]) for i in corpus if p in corpus[i])
        if all(abs(newprob[p] - prob[p]) < 0.001 for p in corpus):
            break
        prob = newprob
    return prob


if __name__ == "__main__":
    main()
