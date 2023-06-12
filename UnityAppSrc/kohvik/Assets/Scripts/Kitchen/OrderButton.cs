using UnityEngine;
using UnityEngine.UI;

public class OrderButton : MonoBehaviour
{
    private Order order;
    private Toggle toggle;
    private Color defaultColor;
    private void Start()
    {
        toggle = transform.GetChild(0).GetComponent<Toggle>();
        ColorBlock cb = toggle.colors;
        defaultColor = cb.normalColor;
        cb.highlightedColor = Color.magenta;
        cb.selectedColor = Color.green;
        toggle.colors = cb;
        toggle.onValueChanged.AddListener(OnToggleValueChanged);
    }

    public Order GetOrder()
    {
        return order;
    }

    public void SetOrder(Order new_order)
    {
        order = new_order;
    }
    public void OnToggleValueChanged(bool isOn)
    {
        ColorBlock cb = toggle.colors;
        if (isOn)
        {
            cb.normalColor = Color.green;
            cb.highlightedColor = Color.blue;
        }
        else
        {
            cb.normalColor = defaultColor;
            cb.highlightedColor = Color.magenta;
        }
        toggle.colors = cb;
    }
}
