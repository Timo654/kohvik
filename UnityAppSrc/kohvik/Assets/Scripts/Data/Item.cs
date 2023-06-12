using System;

// A class to represent an item with ID, name and price
[Serializable]
public class Item
{
    public int ID;
    public string Name;
    public int Price;
    public int Count = 0;

    public override bool Equals(object obj)
    {
        // Perform an equality check on two rectangles (Point object pairs).
        if (obj == null || GetType() != obj.GetType())
            return false;
        Item r = (Item)obj;
        return ID.Equals(r.ID);
    }

    public override int GetHashCode()
    {
        return ID;
    }
}