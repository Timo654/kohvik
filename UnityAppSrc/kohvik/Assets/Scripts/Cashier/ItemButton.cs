using TMPro;
using UnityEngine;

public class ItemButton : MonoBehaviour
{
    private TMP_Text countText;
    private TMP_Text priceText;
    private TMP_Text nameText;
    private Item _item;
    void Awake()
    {
        ItemManager.OnResetCalled += ResetCount;
        countText = transform.Find("Count")?.GetComponent<TMP_Text>();
        nameText = transform.Find("Name").GetComponent<TMP_Text>();
        priceText = transform.Find("Price")?.GetComponent<TMP_Text>();
    }
    public void IncrementCount()
    {
        ItemManager.Instance.AddItemToCart(_item);
        _item.Count++;
        if (countText != null)
            countText.text = _item.Count.ToString();
    }

    public void DecrementCount()
    {
        if (_item.Count > 0)
        {
            ItemManager.Instance.RemoveItemFromCart(_item);
            _item.Count--;
            if (countText != null)
                countText.text = _item.Count.ToString();
        }
    }

    public void SetItem(Item item)
    {
        _item = item;
        UpdateValues();
    }

    private void UpdateValues()
    {
        nameText.text = _item.Name;
        if (priceText != null)
            priceText.text = string.Format("{0:0.00}€", (float)_item.Price / 100);
        ResetCount();
    }

    public void ResetCount()
    {
        _item.Count = 0;
        if (countText != null)
            countText.text = _item.Count.ToString();
    }

    public Item GetItem()
    {
        return _item;
    }
}
