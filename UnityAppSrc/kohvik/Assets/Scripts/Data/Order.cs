using UnityEngine;
using System;
[Serializable]
public class Order
{
    public int ID;
    public Item[] items = null;
    public GameObject orderObject = null;

    public override bool Equals(object obj)
    {
        // Perform an equality check on two rectangles (Point object pairs).
        if (obj == null || GetType() != obj.GetType())
            return false;
        Order r = (Order)obj;
        return ID.Equals(r.ID);
    }

    public override int GetHashCode()
    {
        return ID;
    }
}
