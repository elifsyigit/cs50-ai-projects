import csv
import itertools
import sys

PROBS = {
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },
    "trait": {

        2: {
            True: 0.65,
            False: 0.35
        },

        1: {
            True: 0.56,
            False: 0.44
        },

        0: {
            True: 0.01,
            False: 0.99
        }
    },

    "mutation": 0.01
}


def main():

    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    names = set(people)
    for have_trait in powerset(names):

        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    normalize(probabilities)

    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that:
        * Everyone in `one_gene` has one copy of the gene.
        * Everyone in `two_genes` has two copies of the gene.
        * Everyone not in `one_gene` or `two_genes` has zero copies.
        * Everyone in `have_trait` has the trait.
        * Everyone not in `have_trait` does not have the trait.
    """
    probability = 1  # Start with 1 since we will multiply probabilities

    for person in people:
        if person in one_gene:
            genes = 1
        elif person in two_genes:
            genes = 2
        else:
            genes = 0

        has_trait = person in have_trait

        if people[person]["mother"] is None:
            gene_prob = PROBS["gene"][genes]
        else:
            mother = people[person]["mother"]
            father = people[person]["father"]

            def parent_gene_prob(parent):
                """Compute the probability that a parent passes the gene."""
                if parent in two_genes:
                    return 1 - PROBS["mutation"]  # Always passes gene unless mutation
                elif parent in one_gene:
                    return 0.5  
                else:
                    return PROBS["mutation"] 

            mother_prob = parent_gene_prob(mother)
            father_prob = parent_gene_prob(father)

            if genes == 2:
                gene_prob = mother_prob * father_prob
            elif genes == 1:
                gene_prob = mother_prob * (1 - father_prob) + (1 - mother_prob) * father_prob
            else:
                gene_prob = (1 - mother_prob) * (1 - father_prob)

        trait_prob = PROBS["trait"][genes][has_trait]

        probability *= gene_prob * trait_prob

    return probability


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities:
        if person in one_gene:
            genes = 1
        elif person in two_genes:
            genes = 2
        else:
            genes = 0
        has_trait = person in have_trait
        probabilities[person]["gene"][genes] += p
        probabilities[person]["trait"][has_trait] += p
    


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:
        for a in probabilities[person]:
            t = sum(probabilities[person][a].values())
            for value in probabilities[person][a]:
                probabilities[person][a][value] /= t
    return probabilities


if __name__ == "__main__":
    main()
