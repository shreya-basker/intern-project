from collections import deque
def bfs(graph,start,goal):
    if start==goal:
        return [start]
    
    queue= deque([start])
    visited={start}
    while queue:
        current_path=queue.popleft()
        current_node=current_path[-1]
        if current_node == goal:
            return current_path
        for neighbour in graph.get(current_node,[]):
            if neighbour not in visited:
                visited.add(neighbour)
                new_path=list(current_path)+ [neighbour]
                queue.append(new_path)
    return None
def main():
    graph={ 
    'A': ['B', 'C'], 
    'B': ['D'], 
    'C': ['D', 'E'], 
    'D': ['F'], 
    'E': ['F'], 
    'F': [] 
    }
    shortest_path=bfs(graph,'A','F')
    print(f"The shortest path between A and F is : {shortest_path}")

if __name__=="__main__":
    main()

