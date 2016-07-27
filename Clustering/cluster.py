from math import sqrt
from PIL import Image, ImageDraw

def readfile(file):
    lines = [lines for lines in open(file, encoding='latin-1')]
    column_names = lines[0].strip().split('\t')[1:]
    row_names = []
    data = []
    for line in lines[1:]:
        row_values = line.strip().split('\t')
        row_name = row_values[0]
        row_names.append(row_values[0])
        data.append([float(x) for x in row_values[1:]])
    return row_names, column_names, data


def sim_pearson(var1, var2):
    sum_1 = sum(var1)
    sum_2 = sum(var2)

    sum_1_sqr = sum([pow(v,2) for v in var1])
    sum_2_sqr = sum([pow(v,2) for v in var2])

    sum_product = sum([var1[i]*var2[i] for i in range(len(var1))])

    # Calculate pearson score
    numerator = sum_product - (sum_1 -sum_2/len(var1))
    denominator = sqrt((sum_1_sqr - pow(sum_1,2)/len(var1))*(sum_2_sqr-pow(sum_2, 2)/len(var1)))
    if denominator == 0: return 0

    # Sim Pearson correlation returns a larger values for items that are closer 
    # to each other. 1.0 - sim_pearson results in smaller distances for items that are
    # closer to each other.
    return 1.0 - numerator/denominator

class bicluster:
    def __init__(self, vector, left = None, right = None, distance = 0.0, id = None):
        self.vector = vector
        self.left = left
        self.right = right
        self.distance = distance
        self.id = id

     
def hcluster(rows, distance = sim_pearson):
    distances = {}
    current_cluster_id = -1

    # Intial clusters are just rows

    cluster = [bicluster(rows[i], id = i) for i in range(len(rows))]

    while len(cluster) > 1:
        lowestpair = (0,1)
        closest = distance(cluster[0].vector,cluster[1].vector)

        for i in range(len(cluster)):
            for j in range(i+1, len(cluster)):
                # Cache distance values
                if (cluster[i].id, cluster[j].id) not in distances:
                    distances[(cluster[i].id, cluster[j].id)] = distance(cluster[i].vector, cluster[j].vector)
                d = distances[(cluster[i].id, cluster[j].id)]

                if d < closest:
                    closest = d
                    lowestpair = (i,j)
        # Calculate average of two clusters
        merge_cluster = [(cluster[lowestpair[0]].vector[i] + cluster[lowestpair[1]].vector[i])/2.0 
        for i in range(len(cluster[0].vector))]

        # Create a new cluster
        new_cluster = bicluster(merge_cluster, left = cluster[lowestpair[0]],
                        right = cluster[lowestpair[1]],
                        distance = closest, id = current_cluster_id)

        current_cluster_id -= 1
        # del cluster[lowestpair[0]]
        # del cluster[lowestpair[1]]
        cluster = [cluster[i] for i in range(len(cluster)) if i not in lowestpair]
        cluster.append(new_cluster)
    return cluster[0]

def print_cluster(cluster, labels = None, n = 0):
    for i in range(n):
        print(' ',)
    if cluster.id < 0:
        print('-')
    else:
        if labels == None:
            print(cluster.id)
        else:
            print(labels[cluster.id])
    
    if cluster.left != None: print_cluster(cluster.left, labels = labels, n = n+1)
    if cluster.right != None: print_cluster(cluster.right, labels = labels, n = n+1)

def getheight(cluster):
    """
    Returns the height of the nodes. End point nodes have a height 1.
    Otherwise the height at a node is a sum of the heights of its other branches.
    """
    if cluster.left == None and cluster.right == None: return 1
    return getheight(cluster.left) + getheight(cluster.right)

def getdepth(cluster):
    if cluster.left == None and cluster.right == None: return 0
    return max(getdepth(cluster.left),getdepth(cluster.right)) + cluster.distance

def drawdendrogram(cluster, labels, jpeg = 'cluster.jpeg'):
    height = getheight(cluster) * 20
    width = 1200
    depth = getdepth(cluster)

    scaling = float(width - 150) / depth

    # create new image object with white background
    img = Image.new('RGB', (width,height),(255,255,255))
    draw = ImageDraw.Draw(img)

    draw.line((0, height / 2, 10, height / 2), fill = (0, 0, 0))

    drawnode(draw, cluster, 10, (height / 2), scaling, labels)
    img.save(jpeg, 'JPEG')

def drawnode(draw, cluster, x, y, scaling, labels):
    if cluster.id < 0:
        # If the cluster is not at the endpoints.
        height_1 = getheight(cluster.left) * 20
        height_2 = getheight(cluster.right) * 20
        top = y -(height_1 + height_2) / 2
        bottom = y + (height_1 + height_2) / 2

        ll = cluster.distance * scaling

        # Vertical lines from parent node to child
        draw.line((x, top + height_1/2, x, bottom - height_2/2), fill = (0, 0 ,0 ))

        # Top Horizontal lines from left litems
        draw.line((x, top + height_1/2, x + ll, top + height_1 / 2), fill = (0, 0 ,0))

        # Bottom Horizantal lines
        draw.line((x, bottom - height_2/2, x + ll, bottom - height_2/2), fill = (0, 0, 0))

        # # Call the function to draw left and right nodes
        drawnode(draw, cluster.left, x + ll, top + height_1/2, scaling, labels)
        drawnode(draw, cluster.right, x + ll, bottom - height_2/2, scaling, labels)
    else:
        # if endpoint, draw the item label
        draw.text((x+5, y-7), labels[cluster.id], (0,0,0))

def rotatematrix(data):
    new_data = []
    for i in range(len(data[0])):
        new_row = [data[j][i] for j in range(len(data))]
        new_data.append(new_row)
    return new_data

def main():
    blogsnames, words, data = readfile('./data/blogsdata.txt')
    clust = hcluster(data)
    drawdendrogram(clust, blogsname, jpeg = 'blogcluster.jpg')

if __name__ == "__main__":
    main()
