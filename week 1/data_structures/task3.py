from collections import Counter
def set_functions(list1,list2):
    set1=set(list1)
    set2=set(list2)
    combined_list=list1+list2
    counts=Counter(combined_list)
    #most common elements
    max_frequency=max(counts.values())

    common_elements=[item for item, count in counts.items() if count==max_frequency]

    #unique to each list
    unique_to_list1=set1-set2
    unique_to_list2=set2-set1

    # combine all elements without duplicates
    combined_set=set1|set2

    print(f"Common elements : {common_elements}")
    print(f"Unique to list1 : {unique_to_list1}")
    print(f"Unique to list2 : {unique_to_list2}")
    print(f"Combined set : {combined_set}")

def main():
    list1=[1,2,3,4,5]
    list2=[1,2,6,7,8]
    set_functions(list1,list2)

if __name__== "__main__":
    main()
